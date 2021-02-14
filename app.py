from flask import Flask
from flask import render_template
from flask import request
import connect
import psycopg2
import uuid

dbconn = None


app = Flask(__name__)

def getCursor():
    global dbconn
    if dbconn == None:
        conn = psycopg2.connect(dbname=connect.dbname, user=connect.dbuser, password=connect.dbpass, host=connect.dbhost, port=connect.dbport)
        conn.autocommit = True
        dbconn = conn.cursor()
        return dbconn
    else:
        return dbconn
        
#display all members in the organisation on  homepage 
@app.route("/")
def home():
    cur = getCursor()
    cur.execute("select * from member;")
    select_result = cur.fetchall()
    column_names=[desc[0] for desc in cur.description]
    print(f"{column_names}")
    print(f"{select_result[0]}")
    #display name, date of birth and whether is an adult leader 
    #user selects a member 
    return render_template('memberresult.html', dbresult=select_result, dbcols=column_names[1:])

#after select a member 
@app.route("/member", methods=['GET']) 
def getEventForMember():
    print(request.args) 
    global memberID
    memberID = request.args.get("memberId") 
    print(memberID) 
    cur = getCursor()
    #check whether member is an adult leader 
    cur.execute("select adultleader from member where memberid =%s", (memberID,)) 
    isAdult = cur.fetchall(); 
    print(type(isAdult[0][0]))
    #if member is a youth, display the activity night of groups that the member belongs to
    if(isAdult[0][0] == False): 
        cur = getCursor()
        cur.execute("select activitynightid, nighttitle, activitynightdate, groupname from activitynight an \
inner join activitygroup ag on an.groupid = ag.groupid \
inner join currentgroupmember cgm on ag.groupid = cgm.groupid where cgm.memberid = %s;", (memberID, ))
        select_result = cur.fetchall()
        column_names=[desc[0] for desc in cur.description]
        return render_template('activitynightresult.html', dbresult=select_result, dbcols=column_names[1:])
    else: 
        #if member is adult leader, display the page with functions 
        return render_template("adultresult.html", familyname = familyname)

#direct to this page when youth selects an activity night 
@app.route("/activitynight", methods=['GET']) 
def getAttendee():
    print(request.args) 
    activityNightId = request.args.get("activityNightId") 
    cur = getCursor()
    #display all members belong to this group which the activity night is host for 
    cur.execute("select an.activitynightid, m.memberid, m.familyname, m.firstname from activitynight an \
    inner join currentgroupmember cgm \
    on an.groupid = cgm.groupid \
    inner join member m \
    on cgm.memberid = m.memberid where an.activitynightid =%s", (activityNightId,))
    select_result = cur.fetchall()
    column_names=[desc[0] for desc in cur.description]
    print(f"{column_names}")
    print(f"{select_result[0]}")
    return render_template('groupmemberresult.html', dbresult=select_result, dbcols=column_names[1:])

#direct to this page after youth user select a member from attendee list 
@app.route('/attendee', methods=['GET', 'POST'])
def AddAttendance():
     activityNightId = request.args.get("activityNightId") 
     memberId = request.args.get("memberId") 
     print(activityNightId) 
     print(memberId)
    if request.method == "POST": 
        print(request.form) 
        attendanceStatus = request.form.get("attendanceStatus")
        cur = getCursor()
        cur.execute("INSERT INTO attendance(activitynightid, memberid, attendancestatus) VALUES (%s, %s, %s)", 
        (str(activityNightId),str(memberId),attendanceStatus, )) 
        
        cur.execute("select * from attendance where an.activitynightid =%s and m.memberid =%s", (activityNightId, memberID, )) 
        select_result = cur.fetchall()
        column_names=[desc[0] for desc in cur.description]
        print(f"{column_names}")
        print(f"{select_result[0]}")
        return render_template('attendanceresult.html', dbresult=select_result, dbcols=column_names,)
    else:
        return render_template('attendanceform.html', activityNightID = activityNightId, memberID = memberId)

@app.route("/getgroupattendance") 
def getAttendanceInfo():
    cur = getCursor()
    cur.execute("select cgm.groupid from currentgroupmember cgm inner join member m on m.memberid=cgm.memberid where m.familyname =%s", (familyname,))
    groupid = cur.fetchall()
    print(groupid)
    print(type(groupid))
    newgroupid = ()
    for i in groupid:
        newgroupid = newgroupid + i 
    print(newgroupid)
    cur.execute("select an.nighttitle, m.familyname, m.firstname, at.attendancestatus, at.notes from currentgroupmember cgm \
    inner join activitynight an on an.groupid = cgm.groupid \
    inner join member m on m.memberid = cgm.memberid \
    left join attendance at \
    on at.activitynightid = an.activitynightid where cgm.groupid in %s", (newgroupid,))
    select_result = cur.fetchall()
    column_names=[desc[0] for desc in cur.description]
    print(f"{column_names}")
    print(f"{select_result[0]}")
    return render_template('groupattendance.html', dbresult=select_result, dbcols=column_names)

@app.route('/updateattendance', methods=['GET', 'POST'])
def UpdateAttendance():
    nighttitle = request.args.get("nighttitle", None) 
    familyname = request.args.get("familyname", None)
    print(nighttitle)
    print(familyname)
    cur = getCursor()
    cur.execute("select activitynightid from activitynight where nighttitle = %s", (nighttitle,))
    select_result = cur.fetchall()
    print(select_result)
    print("111111111111111111111111111111111")
    activityNightId = select_result[0][0]
    print(activityNightId)

    cur.execute("select memberid from member where familyname = %s", (familyname,))
    select_result = cur.fetchall()
    memberId = select_result[0][0]
    print(memberId )
    if request.method == "POST": 
        attendanceStatus = request.form.get('attendancestatus') 
        note = request.form.get('note')  
        cur = getCursor()
        cur.execute("select * from attendance where activitynightid = %s and memberid = %s", (activityNightId, memberId, ))
        select_result = cur.execute
        #print(select_result)
        #isAttendanceExist = select_result[0][0]
        #print(isAttendanceExist)
        if select_result == None:
            cur.execute("INSERT INTO attendance(activitynightid, memberid, attendancestatus, notes) VALUES (%s, %s, %s, %s)", 
        (str(activityNightId),str(memberId),attendanceStatus, note, )) 
        else: 
            cur.execute("UPDATE attendance set (attendancestatus = %s, notes = %s) WHERE activitynightid = %s and memberid = %s", 
        (attendanceStatus, note, str(activityNightId),str(memberId), )) 
        
        cur = getCursor()
        cur.execute("select nighttitle, attendancestatus, note from attendance at \
        inner join activitynight an \
        on at.activitynightid = an.activitynightid \
        inner join member m \
        on at.memberid = m.memberid where an.nighttitle =%s and m.memberid =%s", (nighttitle, str(memberId)))
        select_result = cur.fetchall()
        column_names=[desc[0] for desc in cur.description]
        #print(f"{column_names}")
        #print(f"{select_result[0]}")
        return ("/")
    else:
        return render_template('editattendanceform.html')















