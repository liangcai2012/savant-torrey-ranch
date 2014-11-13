from datetime import *
def timeadd(time, sectoadd):
	sec = time%100 + sectoadd
	if sec < 60:
		return time+sectoadd
	else:
		minute = (time%10000)/100 + sec/60
		if minute < 60:
			return (time/10000) * 10000 + minute * 100 + sec%60
		else:
			hour = (time%1000000)/10000 + minute/60
			if hour > 24:
				return -1
			else:
				return (time/1000000) * 1000000 + hour * 10000 + 100 * (minute%60) + sec%60

def timenorm(strtime):
    try:
        utime = int(strtime)
    except ValueError:
        return -1 
    if utime<=24:
        return utime*10000
    elif utime<100:
        return -1 
    elif utime <= 2359:
        if utime%100 > 59:
            return -1 
        return utime*100
    elif utime <10000:
        return -1 
    elif utime <235959:
        if utime%100 > 59:
            return -1 
        if (utime/100)%100 > 59:
            return -1 
        return utime
    else:
        return -1

def tdurnorm(strtdur):
    if strdur[-1] == 'h': 
        eff = 10000
    elif strdur[-1] == 'm':
        eff = 100
    elif strdur[-1] == 's':
        eff = 1
    else:
        return -1

    try:
        udur = int(strdur[:-1])
    except ValueError:
        return -1
    if udur > 59:
        return -1
    return udur*eff


def workdayfind(sdate, delta):
	y = sdate/10000
	m = (sdate%10000)/100
	d = sdate%100

	sday = date(y, m, d)
	tday = sday + timedelta(delta)
	return tday.year*10000 + tday.month*100 + tday.day

def attime2int(time, isdate):
	date = time.year*10000 + time.month*100 + time.day
	if isdate:
		return date 
	else:
		return date*1000000000 + time.hour * 10000000 + time.minute * 100000+time.second *1000 + time.milliseconds

#testing
#print workdayfind(20140323, -189)


	

