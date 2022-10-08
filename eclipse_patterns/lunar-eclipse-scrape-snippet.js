// // #https://eclipse.gsfc.nasa.gov/JLEX/JLEX-AS.html
// // #https://129.164.179.214/JLEX/JLEX-AS.html

// // 129.164.179.214

// ans = [];
// $XX = $x
// btns1 = $x("//input[@type='button']")
// console.log(btns1)
// btns.forEach((x,ix)=>setTimeout((x)=>{
//     console.log(x.value, ans.length, ans.length/18);
//     x.click();
//     var dx = $XX("//*[@id='el_resultstable']//text()")
//     dx.forEach(x=>ans[ans.length] = x.data)
// }
// , 100 * ix, x))

// tbl = []; 
// ans.forEach( (x,i) => {
//     r = Math.floor(i/18); c = i%18; t
//     try { tbl[r].length } catch { tbl[r] =[] } ;  
//     x2 = tbl[r] ; x2[x2.length]=x 
// })


// // https://eclipse.gsfc.nasa.gov/JLEX/JLEX-AS.html
// // Latitude:        9° 54' 00" N
// // Longitude:        78° 66' 00" E
// // Altitude:        0m
// // Time Zone:        05:30 E

ans = [];
$XX = $x
btns1 = $x("//input[@type='button']")
console.log(btns1)
btns1.forEach((x,ix)=>setTimeout((x)=>{
    console.log(x.value, ans.length, ans.length/18);
    x.click();
    var dx = $XX("//*[@id='el_resultstable']//text()")
    dx.forEach(x=>ans[ans.length] = x.data)
}
, 3000 * ix, x))

setTimeout ( () => {
    console.log(ans.length)
    tbl = []; 
    ans.forEach( (x,i) => {
        r = Math.floor(i/18); c = i%18; 
        try { tbl[r].length } catch { tbl[r] =[] } ;  
        x2 = tbl[r] ; x2[x2.length]=x 
    })
    let csv = tbl.map (x => x.join(",")).join("\n")
    console.log(csv)
} ,  (btns1.length + 3)*3000 )