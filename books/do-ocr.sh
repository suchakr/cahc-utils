#!/bin/bash
already="already"
RAW=01_raw_pdf
SRCH=02_srch_pdf
RAWPAGE=03_raw_page_pdf
SRCHPAGE=04_srch_page_pdf
PNGPAGE=05_raw_page_png
TILEPNG=06_tile_png
OCRSNIPS=07_ocr_snips

[ -d $SRCH ] || mkdir -p $SRCH
echo "Making searchable pdf"
for ff in $RAW/*.pdf; do 
	f=$(basename -- "$ff")
	f=$SRCH/$f
	already="already"
	if [ ! -e $f ]; then
		qpdf --decrypt $ff .x2.pdf
		echo ocrmypdf .x2.pdf  $f
		ocrmypdf -q .x2.pdf $f
		rm .x2.pdf
		already=""
	fi 
	echo "	$f generated $already" 
done
echo ""

[ -d $RAWPAGE ] || mkdir -p $RAWPAGE
echo "Splitting raw pdf pages"
for ff in $RAW/*.pdf; do 
	f=$(basename -- "$ff")
	f=$RAWPAGE/$f
	f=${f/.pdf/}
	if [ ! -e $f-001.pdf ]; then
		echo "	pdfseparate $ff $f-%03d.pdf"
		pdfseparate $ff $f-%03d.pdf
		echo "	" ` ls $f* | wc -l` "$f\*" 
		ls -las $f* | grep -v ^d |  head -3
		ls -las $f* | grep -v ^d |  tail -3
		echo ""
	fi 
done
echo "	" `ls $RAWPAGE | wc -l`  " files in $RAWPAGE"
echo ""


[ -d $SRCHPAGE ] || mkdir -p $SRCHPAGE
echo "Splitting raw pdf pages"
for ff in $SRCH/*.pdf; do 
	f=$(basename -- "$ff")
	f=$SRCHPAGE/$f
	f=${f/.pdf/}
	if [ ! -e $f-001.pdf ]; then
		echo "	pdfseparate $ff $f-%03d.pdf"
		pdfseparate $ff $f-%03d.pdf
		echo "	" ` ls $f* | wc -l` "$f\*" 
		ls -las $f* | grep -v ^d |  head -3
		ls -las $f* | grep -v ^d |  tail -3
		echo ""
	fi 
done
echo "	" `ls $SRCHPAGE | wc -l`  " files in $SRCHPAGE"
echo ""

[ -d $PNGPAGE ] || mkdir -p $PNGPAGE
echo "Png-fication + Crop of raw pdf pages"
for ff in $RAWPAGE/*.pdf; do 
	f=$(basename -- "$ff")
	f=$PNGPAGE/$f
	f=${f//pdf/}png
	if [ ! -e $f ] ; then
		echo "	sips -s format png $ff --out crop.png" 
		sips -s format png $ff --out crop.png
		echo "	ffmpeg -i crop.png -vf  \"crop=1120:1490:55:85\" $f "
		ffmpeg -loglevel error -i crop.png -vf  "crop=1120:1490:55:85" $f 
		rm crop.png
	fi 
done
echo "	" `ls $PNGPAGE | wc -l`  " files in $PNGPAGE"
echo ""

[ -d $TILEPNG ] || mkdir -p $TILEPNG
echo "Extract Voter Tile pngs"
for ff in $PNGPAGE/*png; do
	f=$(basename -- "$ff")
	f=$TILEPNG/$f
	f=${f/.png/}
	if [ ! -e $f-001.png ]; then 
		echo "ffmpeg -loop 1 -i $ff -vf \"crop=iw/3:ih/10:mod(n\,3)*iw/3:trunc(n/3*ih/10)\" -vframes 30 $f-%03d.png"
		ffmpeg -loglevel error -loop 1 -i $ff -vf "crop=iw/3:ih/10:mod(n\,3)*iw/3:trunc(n/3*ih/10)" -vframes 30 $f-%03d.png
		echo ""
	fi
done
echo "	" `ls $TILEPNG | wc -l`  " files in $TILEPNG"
echo ""

[ -d $OCRSNIPS ] || mkdir -p $OCRSNIPS
echo "OCR Tiles"
for ff in $TILEPNG/*png; do
	f=$(basename -- "$ff")
	f=$OCRSNIPS/$f
	f=${f/.png/}
	if [ -e $f.txt.txt ] ; then
		mv $f.txt.txt $f.txt
	fi
	if [ ! -e $f.txt ]; then 
		echo "tesseract -l eng $ff $f"
		tesseract -l eng $ff $f
		echo ""
	fi
done
echo "	" `ls $OCRSNIPS | wc -l`  " files in $OCRSNIPS"
echo ""


OCRNAMES=ocr_names.html
if [ -e $OCRNAMES ] ; then
	rm $OCRNAMES
fi
echo "<html>" >> $OCRNAMES
for ff in `grep -ln "Name" 07_ocr_snips/*` ; do 
	f=$(basename -- "$ff")
	baretile=${f/.txt/}
	barepng=`echo $baretile | perl -pe 's/....$//'`
	png=$PNGPAGE/${barepng}.png
	pdf=$SRCHPAGE/${barepng}.pdf
	tile=$TILEPNG/${baretile}.png
	echo "<table style=\"border:1px solid black;border-collapse:collapse\"><tr>" >> $OCRNAMES
	echo "<td colspan=2 style=\"background:lightgray\"><center><h2> $baretile </h2><center></td></tr><tr>" >> $OCRNAMES
	echo "<td style=\"background:yellow; padding:5px\"><pre>" >> $OCRNAMES
	cat $ff  >> $OCRNAMES
	echo "" >> $OCRNAMES
	echo "" >> $OCRNAMES
	echo "</pre></td>" >> $OCRNAMES
	echo "<td><b> See page ${barepng} as </b>: " >> $OCRNAMES
	## echo "<a href="$png"> PNG </a> &nbsp;" >> $OCRNAMES
	echo "<a href="$pdf"> Searchable-PDF </a><br>" >> $OCRNAMES
	echo "<img src="$tile" alt="$tile"/><br></td>" >> $OCRNAMES
	echo "</tr></table><br>" >> $OCRNAMES
done
echo "</html>" >> $OCRNAMES
head $OCRNAMES




# PDFDIR="pdf-pages"
# for  LOCN in ./ ./$PDFDIR; do
# echo Generation $PDFDIR
# if [ ! -d $PDFDIR ]; then 
# 	already=""
# 	[ -d $PDFDIR ] || mkdir -p $PDFDIR 
# 	for f in *pdf; do 
# 		d=${f/.pdf/};  
# 		echo pdfseparate ${LOCN}$f $PDFDIR/$d-%03d.pdf;
# 		pdfseparate $f $PDFDIR/$d-%03d.pdf;
# 	done
# 	fi
# echo `ls $PDFDIR | wc -l` "pages in $PDFDIR/ $aready"
# 
# PDFDIR="pdf-pages"
# echo Generation $PDFDIR
# if [ ! -d $PDFDIR ]; then 
# 	already=""
# 	[ -d $PDFDIR ] || mkdir -p $PDFDIR 
# 	for f in *pdf; do 
# 		d=${f/.pdf/};  
# 		echo pdfseparate $f $PDFDIR/$d-%03d.pdf;
# 		pdfseparate $f $PDFDIR/$d-%03d.pdf;
# 	done
# 	fi
# echo `ls $PDFDIR | wc -l` "pages in $PDFDIR/ $aready"


#[-d png-pages] || mkdir -p png-pages
#for f in pdf-pages/*.pdf; do sips -s format png $f  --out "${f//pdf/png}"; done

#for f in png-pages/*.png; do
#	c=${} ;
#	ffmpeg -i $f -vf  "crop=1120:1490:55:85" crop.png;
#	ffmpeg -loop 1 -i crop.png -vf "crop=iw/3:ih/10:mod(n\,3)*iw/3:trunc(n/3*ih/10" -vframes 30 png-crops/%03d.png #ok
#done


#ffmpeg -i S10A174P441-junna.png-008.png -vf  "crop=1120:1490:55:85" crop2.png #ok
#tesseract -l eng 08out001.png aaaout001.png #ok
