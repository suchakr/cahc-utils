include("nakshatras.inc");
function r(x) { return Math.round(100 * x) / 100 }
function r3(x) { return Math.round(1000 * x) / 1000 }
core.setObserverLocation(76 + 52 / 60 + 47.99 / 3600, 29 + 57 / 60 + 36 / 3600, 1, "कुरुक्षेत्र", "Earth")
// BHA_FIRST_VISIBILITY_1500BCE = 1173273.52758 // -1500-04-01T05:47:13

MarkerMgr.deleteAllMarkers()
LabelMgr.deleteAllLabels()


header = 'mars Jyes diff dt'
say(header.split(/\s+/).join("\t"))
warn(header.split(/\s+/).join("\t"))


jds = [1502607.5, 1503314.5, 1504028.5, 1504735.5, 1505442.5, 1506149.5, 1506688.5,
    1507381.5, 1508088.5, 1508802.5, 1509509.5, 1510223.5, 1510930.5, 1511637.5,
    1512204.5, 1512876.5, 1513576.5, 1514290.5, 1514997.5, 1515711.5, 1516418.5,
    1517125.5, 1517832.5, 1518364.5, 1519064.5, 1519771.5, 1520485.5, 1521192.5,
    1521906.5, 1522613.5, 1523320.5, 1523859.5, 1524552.5, 1525259.5, 1525973.5,
    1526680.5, 1527394.5, 1528101.5, 1528808.5, 1529508.5, 1530047.5, 1530747.5,
    1531454.5, 1532168.5, 1532882.5, 1533589.5, 1534296.5, 1535003.5, 1535535.5,
    1536235.5, 1536942.5, 1537656.5, 1538363.5,
]

var tk = new TimeKeeper()
for (i = 0; i < jds.length; i++) {

    gaps = []
    for (step = -3; step < 8; step++) {
        jd = jds[i] + step; JD(jd); W(.2); dt = DT()
        mars = getOI('Mars').elong; W(.2)
        jyeshta = getOI('α Sco').elong; W(.2)
        gap = r(mars - jyeshta)
        gap = gap < 0 ? -gap : gap
        gaps[gaps.length] = gap
        //ddump (gaps)
        if (gaps.length >= 3) {
              //say("3+")
              //ddump(gaps) 

              c0 = gaps[gaps.length-1]  ;c1 = gaps[gaps.length-2] ; c2=gaps[gaps.length-3]

              ddump([ c0,c1,c2])
              ddump([(c1<=c0) , (c1<=c2)] )
              
		if ([(c1<=c0) && (c1<=c2)] )  { 
			say([r(mars), r(jyeshta), r(mars - jyeshta), dt].join("\t"))
		}
        }
    }
    say("======")
}

