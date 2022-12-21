// http://astropixels.com/ephemeris/phasescat/phasescat.html
ans = [];
$XX = $x
btns1 = $x("//input[@type='button']")
console.log(btns1)
// btns1.forEach((x,ix)=>setTimeout((x)=>{
//     console.log(x.value, ans.length, ans.length/18);
//     x.click();
//     var dx = $XX("//*[@id='el_resultstable']//text()")
//     dx.forEach(x=>ans[ans.length] = x.data)
// }
// , 3000 * ix, x))

// setTimeout ( () => {
//     console.log(ans.length)
//     tbl = []; 
//     ans.forEach( (x,i) => {
//         r = Math.floor(i/18); c = i%18; 
//         try { tbl[r].length } catch { tbl[r] =[] } ;  
//         x2 = tbl[r] ; x2[x2.length]=x 
//     })
//     let csv = tbl.map (x => x.join(",")).join("\n")
//     console.log(csv)
// } ,  (btns1.length + 3)*3000 )
