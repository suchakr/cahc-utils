https://www.tropmet.res.in/data/data-archival/rain/Readme.pdfThis document was last updated on August 29, 2017. Copy Right:
Indian Institute of Tropical Meteorology (IITM) Homi Bhabha Road
Pune 411 008, India
The accompanying data as described below may be freely used and redistributed for non-profit and non-commercial research purposes, provided IITM is duly acknowledged as the data source. Any redistribution should necessarily include this document.
Title:
IITM Indian regional/subdivisional Monthly Rainfall data set (IITM-IMR)
Contributors:
D.A. Mooley
B. Parthasarathy K. Rupa Kumar N.A. Sontakke A.A. Munot D.R. Kothawale
M.Rajeevan Primary Data Source:
India Meteorological Department Data Period:
1871-2016 Accompanying Data Files:
iitm-imr-stn.txt (List of 306 raingauge stations used)
iitm-regionrf.txt.gz (Monthly rainfall for homogeneous regions) iitm-subdivrf.txt.gz (Monthly rainfall of 30 meteorological subdivisions)
Data Format:
Data are arranged region/subdivisionwise, with a header record for each region/subdivision followed by 146 data records each

C C
record containing data for one year (12 months and 5 seasons values) . The following FORTRAN code extract leads to rainfall in mm/month
(Data have a resolution of up to 0.1 mm/month).
do is=i,nsets read(5,1)nyears,details 1 format(i3,a,/////)
do iy=1,nyears
read(5,2)iyear,(rf(is,iy,m),m=1,17) 2 format(i4,1x,17f6.1)
enddo
Rainfall statistics read(5,3)detail1
3 format(a,//)
monthly and seasonal rainfall statistics do I=1,4
read(5,4)st, (std(I,J),J=1,17)
4 format(a5,12f6.1) enddo
read(5,5)detail2 5 format(a)
enddo
The character variable 'details' contains the following: iitm-regionrf.txt:
Name of the region;
Data Period;
Number of subdivisions included; Area of the region in sq. km.
iitm-subdivrf.txt:
Numerical Code of the subdivision;
Name of the subdivision;
Area of the subdivision in sq.km.;
Percentage of the area out of the total area of the country; Number of stations used to compute the spatial mean; Data period.
Data Description:
Network of rain-gauge stations:
While selecting the network of rain-gauge stations, an

effort was made to select a network which would provide one representative station per district having a reliable record
for the longest possible period. The network selected under these constraints consist of 306 almost uniformly distributed stations for which rainfall data are available from 1871. The hilly regions consisting of four meteorological subdivisions
of India which are parallel to Himalayan mountain range have not been considered in view of the meagre rain-gauge network and low areal representation of a rain-gauge in a hilly area. Two island subdivisions far away from mainland have also not been included. Thus, the contiguous area having network of 306 stations over 30 meteorological subdivisions measures about 2,880,000 sq.km., which is about 90 percent of the total area
of the country.
Preparation of Subdivisional/Regional rainfall series
The monthly (January - December) area weighted rainfall series for each of the 30 meteorological subdivisions have
been prepared by assigning the district area as the weight for each rain-gauge station in that subdivision. Similarly assigning the subdivision area as the weight to each of the subdivisions in the region, area weighted monthly rainfall series are prepared for Homogeneous regions of India as well as for all India.
IMPORTANT NOTE:
The data for the recent period 2015-2016 are preliminary estimates based on the subdivisional means supplied by the India Meteorlogical Department (IMD), which are in turn based on a variable network. However, the IMD data have been rescaled to conform to the long-term
means of the respective subdivisions in the IITM-IMR data set. These data will be updated as and when the full set of data for 306 stations becomes available.
Quality Control
Quality control measures were also taken up to identify outliers/errors in data archival process, such as keying or printing mistakes. The following procedures were followed to identify outliers/errors in the data sets.
 The monthly rainfall values for individual stations that differ from their corresponding long term means by more than four times their standard deviation were listed .
 The monthly rainfall of some of the 306 stations are reported in the IDWR and identified outlier values of these stations were checked from it and ensured, and finally outlier values were replaced by IDWR values. However, for some of the stations data are not

reported in the IDWR, rainfall data of such stations were checked with rainfall of surrounding stations as well as percentage departure of respective sub-divisional rainfall. The synoptic systems during that month over that region have also been checked. If the identified outlier value is consistent with surrounding stations rainfall values and the respective station sub-divisional percentage departure rainfall of that month, then it is not treated as outlier. The identified outlier values were put as missing (-99.9), and those values were interpolated as discussed in IITM Research Report No. RR-138..During keying the data, the rainfall of very few stations for monsoon months (June-September) were wrongly reported as zero. For these stations, location of station and monsoon onset dates were checked for June and July months, and for August and September values were checked as per method discussed in IITM Research Report No. RR-138 and finally these values were interpolated as per above technique.
Preparation of All-India, Homogeneous region and Sub-divisional rainfall series
The Meteorological subdivisions into which the country has been divided. Area weighted mean monthly rainfall (January through December ) for each of the 30 meteorological subdivisions have been prepared by assigning the district area as a weight for each respective rain gauge station for the period 1871-2014. However, for very few subdivisions, availability of stations data for the years 2013 and 2014 were not sufficient ( less than 80 % of total stations available in the subdivisions). Hence, the sub-divisional rainfall for those years were constructed by using IMD sub-divisional rainfall data as procedure given by Parthasarthy et al. 1992 (a), and and these years were also mentioned in respective sub-divisional rainfall time series listing as well as in corresponding figure. For the years 2015 and 2016, monthly rainfall of all the 306 stations are not readily available. Hence, the rainfall series of 2015 and 2016 of all the subdivisions were prepared from IMD sub divisional rainfall as mentioned above.
Key References
Mooley, D. A., Parthasarathy, B., Sontakke, N. A., and Munot, A. A 1981 : Annual rain-water over India, its variability and impact on the economy. J. Climatol, 1, 167-186.
Parthasarathy, B., Sontakke, N. A., Munot, A. A. and Kothawale, D. R. 1987: Droughts/floods in the summer monsoon rainfall season over different meteorological subdivisions of India for the period 1871-1984. J. Climatol, 7, 57-70.
Parthasarathy, B., Rupa Kumar, K and Munot, A. A. 1993 : Homogeneous Indian Monsoon Rainfall : variability and prediction. Proc. Indian Acad. Sci. (Earth Planet. Sci.) 121-155.
Parthasarathy B., Munot A.A., Kothawale D.R., 1995. All India monthly and seasonal rainfall series : 1871-1993. Theor. and Appl. Climatol., 49, 217-224.
Parthasarathy B., Munot A.A., Kothawale D.R., 1995. Monthly and

seasonal rainfall series for all-India homogeneous regions and meteorological subdivisions : 1871-1994. Research Report No. RR-065, Indian Institute of Tropical Meteorology, Pune, 113pp.
Pant, G.B. and Rupa Kumar, K., 1997. Climates of South Asia. John Wiley & Sons, Chichester, 320 pp.
Kothawale D.R., Rajeevan M., Monthly, Seasonal and Annual Rainfall Time Series for All- India, Homogeneous Regions and Meteorological Subdivisions: 1871-2016, IITM Research Report No. RR-138, August 2017
Feedback:
Please direct questions/problems and requests for updates to
Dr. D.R. Kothawale
Scientist-E (Retd.)
Indian Institute of Tropical Meteorology Homi Bhabha Road
Pune 411 008, India
email: kothawaledrk1957@gmail.com M. No. : +91-9850340433
OR
Dr. Rupa Kumar Kolli
Former Chief, World Climate Applications & CLIPS Divisions, WMO, Geneva
M. No. : +91-9922597262
email: rkolli.wmo@gmail.com

This document was last updated on August 29, 2017. Copy Right:
Indian Institute of Tropical Meteorology (IITM) Homi Bhabha Road
Pune 411 008, India
The accompanying data as described below may be freely used and redistributed for non-profit and non-commercial research purposes, provided IITM is duly acknowledged as the data source. Any redistribution should necessarily include this document.
Title:
IITM Indian regional/subdivisional Monthly Rainfall data set (IITM-IMR)
Contributors:
D.A. Mooley
B. Parthasarathy K. Rupa Kumar N.A. Sontakke A.A. Munot D.R. Kothawale
M.Rajeevan Primary Data Source:
India Meteorological Department Data Period:
1871-2016 Accompanying Data Files:
iitm-imr-stn.txt (List of 306 raingauge stations used)
iitm-regionrf.txt.gz (Monthly rainfall for homogeneous regions) iitm-subdivrf.txt.gz (Monthly rainfall of 30 meteorological subdivisions)
Data Format:
Data are arranged region/subdivisionwise, with a header record for each region/subdivision followed by 146 data records each

C C
record containing data for one year (12 months and 5 seasons values) . The following FORTRAN code extract leads to rainfall in mm/month
(Data have a resolution of up to 0.1 mm/month).
do is=i,nsets read(5,1)nyears,details 1 format(i3,a,/////)
do iy=1,nyears
read(5,2)iyear,(rf(is,iy,m),m=1,17) 2 format(i4,1x,17f6.1)
enddo
Rainfall statistics read(5,3)detail1
3 format(a,//)
monthly and seasonal rainfall statistics do I=1,4
read(5,4)st, (std(I,J),J=1,17)
4 format(a5,12f6.1) enddo
read(5,5)detail2 5 format(a)
enddo
The character variable 'details' contains the following: iitm-regionrf.txt:
Name of the region;
Data Period;
Number of subdivisions included; Area of the region in sq. km.
iitm-subdivrf.txt:
Numerical Code of the subdivision;
Name of the subdivision;
Area of the subdivision in sq.km.;
Percentage of the area out of the total area of the country; Number of stations used to compute the spatial mean; Data period.
Data Description:
Network of rain-gauge stations:
While selecting the network of rain-gauge stations, an

effort was made to select a network which would provide one representative station per district having a reliable record
for the longest possible period. The network selected under these constraints consist of 306 almost uniformly distributed stations for which rainfall data are available from 1871. The hilly regions consisting of four meteorological subdivisions
of India which are parallel to Himalayan mountain range have not been considered in view of the meagre rain-gauge network and low areal representation of a rain-gauge in a hilly area. Two island subdivisions far away from mainland have also not been included. Thus, the contiguous area having network of 306 stations over 30 meteorological subdivisions measures about 2,880,000 sq.km., which is about 90 percent of the total area
of the country.
Preparation of Subdivisional/Regional rainfall series
The monthly (January - December) area weighted rainfall series for each of the 30 meteorological subdivisions have
been prepared by assigning the district area as the weight for each rain-gauge station in that subdivision. Similarly assigning the subdivision area as the weight to each of the subdivisions in the region, area weighted monthly rainfall series are prepared for Homogeneous regions of India as well as for all India.
IMPORTANT NOTE:
The data for the recent period 2015-2016 are preliminary estimates based on the subdivisional means supplied by the India Meteorlogical Department (IMD), which are in turn based on a variable network. However, the IMD data have been rescaled to conform to the long-term
means of the respective subdivisions in the IITM-IMR data set. These data will be updated as and when the full set of data for 306 stations becomes available.
Quality Control
Quality control measures were also taken up to identify outliers/errors in data archival process, such as keying or printing mistakes. The following procedures were followed to identify outliers/errors in the data sets.
 The monthly rainfall values for individual stations that differ from their corresponding long term means by more than four times their standard deviation were listed .
 The monthly rainfall of some of the 306 stations are reported in the IDWR and identified outlier values of these stations were checked from it and ensured, and finally outlier values were replaced by IDWR values. However, for some of the stations data are not

reported in the IDWR, rainfall data of such stations were checked with rainfall of surrounding stations as well as percentage departure of respective sub-divisional rainfall. The synoptic systems during that month over that region have also been checked. If the identified outlier value is consistent with surrounding stations rainfall values and the respective station sub-divisional percentage departure rainfall of that month, then it is not treated as outlier. The identified outlier values were put as missing (-99.9), and those values were interpolated as discussed in IITM Research Report No. RR-138..During keying the data, the rainfall of very few stations for monsoon months (June-September) were wrongly reported as zero. For these stations, location of station and monsoon onset dates were checked for June and July months, and for August and September values were checked as per method discussed in IITM Research Report No. RR-138 and finally these values were interpolated as per above technique.
Preparation of All-India, Homogeneous region and Sub-divisional rainfall series
The Meteorological subdivisions into which the country has been divided. Area weighted mean monthly rainfall (January through December ) for each of the 30 meteorological subdivisions have been prepared by assigning the district area as a weight for each respective rain gauge station for the period 1871-2014. However, for very few subdivisions, availability of stations data for the years 2013 and 2014 were not sufficient ( less than 80 % of total stations available in the subdivisions). Hence, the sub-divisional rainfall for those years were constructed by using IMD sub-divisional rainfall data as procedure given by Parthasarthy et al. 1992 (a), and and these years were also mentioned in respective sub-divisional rainfall time series listing as well as in corresponding figure. For the years 2015 and 2016, monthly rainfall of all the 306 stations are not readily available. Hence, the rainfall series of 2015 and 2016 of all the subdivisions were prepared from IMD sub divisional rainfall as mentioned above.
Key References
Mooley, D. A., Parthasarathy, B., Sontakke, N. A., and Munot, A. A 1981 : Annual rain-water over India, its variability and impact on the economy. J. Climatol, 1, 167-186.
Parthasarathy, B., Sontakke, N. A., Munot, A. A. and Kothawale, D. R. 1987: Droughts/floods in the summer monsoon rainfall season over different meteorological subdivisions of India for the period 1871-1984. J. Climatol, 7, 57-70.
Parthasarathy, B., Rupa Kumar, K and Munot, A. A. 1993 : Homogeneous Indian Monsoon Rainfall : variability and prediction. Proc. Indian Acad. Sci. (Earth Planet. Sci.) 121-155.
Parthasarathy B., Munot A.A., Kothawale D.R., 1995. All India monthly and seasonal rainfall series : 1871-1993. Theor. and Appl. Climatol., 49, 217-224.
Parthasarathy B., Munot A.A., Kothawale D.R., 1995. Monthly and

seasonal rainfall series for all-India homogeneous regions and meteorological subdivisions : 1871-1994. Research Report No. RR-065, Indian Institute of Tropical Meteorology, Pune, 113pp.
Pant, G.B. and Rupa Kumar, K., 1997. Climates of South Asia. John Wiley & Sons, Chichester, 320 pp.
Kothawale D.R., Rajeevan M., Monthly, Seasonal and Annual Rainfall Time Series for All- India, Homogeneous Regions and Meteorological Subdivisions: 1871-2016, IITM Research Report No. RR-138, August 2017
Feedback:
Please direct questions/problems and requests for updates to
Dr. D.R. Kothawale
Scientist-E (Retd.)
Indian Institute of Tropical Meteorology Homi Bhabha Road
Pune 411 008, India
email: kothawaledrk1957@gmail.com M. No. : +91-9850340433
OR
Dr. Rupa Kumar Kolli
Former Chief, World Climate Applications & CLIPS Divisions, WMO, Geneva
M. No. : +91-9922597262
email: rkolli.wmo@gmail.com

