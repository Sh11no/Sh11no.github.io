import requests
import time
import json
import random
import warnings

warnings.filterwarnings('ignore')

sessions = requests.session()
login_campusId = ''
current_semester_id = ''
login_accessToken = ''
login_tokenType = ''
login_organizationId = ''
login_id = ''

def generateroute():
    def generatecenter(A, B):
        import random
        random.seed()
        x = random.randint(0, 10) / 10
        random.seed()
        y = random.randint(0, 10) / 10
        vectori = (-0.0054138452999, -0.0018370139347)
        vectorj = (-0.0032913788853, 0.0069236650781)
        A = A + (x * vectori[0] + y * vectorj[0])
        B = B + (x * vectori[1] + y * vectorj[1])
        return A, B
    E = (30.7555451342275, 103.9281305292315)
    R = 0.003339756
    M, N = generatecenter(E[0], E[1])
    y = random.randint(1, 2 * R * 1E9) * pow(10, -9) + (N - R)
    x = pow((R * R - (y - N) * (y - N)), 0.5) + M
    def solution(y):
        a = pow(R * R - (y - N) * (y - N), 0.5)
        return a
    def nextpoint(x, y):
        d = 0.000095859
        k = -(x - M) / (y - N)
        if k > 0:
            if y < N:
                y = k * (-d) + y
                x = solution(y) + M
            else:
                y = k * d + y
                x = -solution(y) + M
        if k < 0:
            if y < N:
                y = k * (-d) + y
                x = -solution(y) + M
            else:
                y = k * d + y
                x = solution(y) + M
        return x, y
    route = []
    for i in range(300):
        x, y = nextpoint(x, y)
        if y <= N - R:
            y = N - R + 0.0001
            x = -pow((R * R - (y - N) * (y - N)), 0.5) + M
        if y >= N + R:
            y = N + R - 0.0001
            x = pow((R * R - (y - N) * (y - N)), 0.5) + M
        route.append({"latitude": x, "longitude": y})
    return route

def getCurrent():
    global current_semester_id
    url = "https://cpes.legym.cn/education/semester/getCurrent"
    print("[+] Start getting Current.")
    headers = {
        'Authorization': login_tokenType + ' ' + login_accessToken,
        'Organization': login_organizationId,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; PEEM00 Build/RKQ1.201105.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/32.0)'
    }
    resp = sessions.get(url, headers=headers, verify=False)
    current_json = json.loads(resp.content.decode('utf-8'))
    print("[+] current_json:")
    print(current_json)
    current_semester_id = current_json['data']['id']
    print("[+] Got current semester id:" + current_semester_id)
    print("")
    return current_json

def login():
	global login_tokenType
	global login_campusId
	global login_accessToken
	global login_organizationId
	global login_id
	headers = {
		'Authorization': '',
		'Organization': '',
		'Content-Type': 'application/json',
		'User-Agent': 'Mozilla/5.0 (Linux; Android 11; PEEM00 Build/RKQ1.201105.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/32.0)'
	}
	print("请登录乐健体育")
	username = input("Username:")
	password = input("Password:")
	data = {
		'entrance': '1',
		'password': password,
		'userName': username
	}

	url = 'https://cpes.legym.cn/authorization/user/manage/login'
	resp = sessions.post(url, data=json.dumps(data), headers=headers, verify=False)
	login_json = json.loads(resp.content.decode('utf-8'))
	if login_json['code'] != 0:
		print("[!] Login Failed.")
		print(login_json)
		return login_json
	login_campusId = login_json['data']['campusId']
	login_accessToken = login_json['data']['accessToken']
	login_tokenType = login_json['data']['tokenType']
	login_organizationId = login_json['data']['organizationId']
	login_id = login_json['data']['id']

	print("[+] Login succeeded.")
	print("[+] CampusId:" + login_campusId)
	print("[+] accessToken:" + login_accessToken)
	print("[+] tokenType:" + login_tokenType)
	print("[+] organizationId:" + login_organizationId)
	print("[+] Id:" + login_id)
	#print(login_json)
	print("=" * 64)
	print("Welcome, " + login_json['data']['realName'] + " from " + login_json['data']['schoolName'] + login_json['data']['organizationName'])
	print("学号: " + login_json['data']['organizationUserNumber'])
	print("=" * 64)
	return login_json

def getRunningLimit():
    url = 'https://cpes.legym.cn/running/app/getRunningLimit'
    headers = {
        'Authorization': login_tokenType + ' ' + login_accessToken,
        'Organization': login_organizationId,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; PEEM00 Build/RKQ1.201105.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/32.0)'
    }
    data = {
        'semesterId': current_semester_id
    }
    resp = sessions.post(url, data=json.dumps(data), headers=headers, verify=False)
    return json.loads(resp.content.decode('utf-8'))

def run():
	print("[+] Getting running limit.")
	Limit = getRunningLimit()
	limitationsGoalsSexInfoId = Limit['data']['limitationsGoalsSexInfoId']
	print("[+] Got limitationsGoalsSexInfoId.")
	print(limitationsGoalsSexInfoId)
	print("")
	print("[+] Running started.")
	url = 'https://cpes.legym.cn/running/app/uploadRunningDetails'
	headers = {
        'Authorization': login_tokenType + ' ' + login_accessToken,
		'Content-Type': 'application/json',
		'User-Agent': 'okhttp/4.2.2'
	}
	random.seed()
	distance = 3.0 + random.randint(0, 80) / 1000
	random_duration = int(random.uniform(1050 / 3.5 * distance, 1900 / 3.5 * distance))
	begin_time = time.localtime(time.time() - random_duration)
	end_time = time.localtime()
	random.seed()
	data = {
		"scoringType": 1,
 		"semesterId": current_semester_id,
		"signPoint": [],
		"startTime": time.strftime("%Y-%m-%d %H:%M:%S", begin_time),
		"totalMileage": distance,
		"totalPart": 0.0,
		"type": "自由跑",
		"uneffectiveReason": "",
		"avePace": random_duration / distance * 1000 + random.randint(0, 1) / 10,
		"calorie": int(distance * random.uniform(75.9, 76.5)),
		"effectiveMileage": distance,
		"effectivePart": 1,
		"endTime": time.strftime("%Y-%m-%d %H:%M:%S", end_time),
		"gpsMileage": distance,
		"limitationsGoalsSexInfoId": (limitationsGoalsSexInfoId),
		"paceNumber": distance * (1000 - random.randint(50, 156)),
		"paceRange": random.randint(4, 10),
		"routineLine": generateroute()
	}
	#print(data)
	resp = sessions.post(url, data=json.dumps(data), headers=headers, verify=False)
	print(json.loads(resp.content.decode('utf-8')))
	return 0


login()
getCurrent()
run()
print("[+] Running succeeded, maybe. See Lejian?")