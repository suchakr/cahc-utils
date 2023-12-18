// Set the resolution of the sphere
$fn = 50;
deg = $t*360;

naks = [ 
    "Ashwini" , "Bharani" , "Krittika" , "Rohini" , "Mrigashīrsha" , "Ārdrā" , 
    "Punarvasu" , "Pushya" , "Āshleshā" , "Maghā" , "Pūrva Phalgunī" , 
    "Uttara Phalgunī" , "Hasta" , "Chitra" , "Svātī" , "Vishākhā" , 
    "Anurādhā" , "Jyeshtha" , "Mūla" , "Pūrva Ashādhā" , "Uttara Ashādhā" , 
    "Shravana" , "Shravishthā" , "Shatabhisha" , "Pūrva Bhādrapadā" , 
    "Uttara Bhādrapadā" , "Revatī" ];

naks_sans = [ "अश्विनि" , "भरणी" , "कृत्तिका" , "रोहिणी" , "मृगशीर्षा" , "आर्द्रा" , 
    "पुनर्वसु" , "पुष्य" , "आश्लेषा" , "मघा" , "पूर्व फल्गुनी" , 
    "उत्तर फल्गुनी" , "हस्त" , "चित्रा" , "स्वाति" , "विशाखा" , 
    "अनुराधा" , "ज्येष्ठा" , "मूल" , "पूर्वाषाढ़ा" , "उत्तराषाढ़ा" , 
    "श्रवण" , "श्रविष्ठा" , "शतभिषा" , "पूर्व भाद्रपदा" , 
    "उत्तर भाद्रपदा" , "रेवती" ];

echo (deg, len(naks), deg/len(naks), $t*27);
nak = naks[deg/len(naks)];
// deg = round(deg);
{
// Draw a transparent sphere with radius 10 - sky
%color([1, 1, 1, 0.2]) sphere(r = 10);

// Draw a point at the center of the sphere - earth
color([0, 0, 1, 0.5]) sphere(r = .5);

// Draw an equatorial plane 
color([1, 0, 1, 0.5]) difference() { 
    cylinder(h=.1, r=10.5, center=true);
    cylinder(h=.11, r=10.1, center=true);

}

// Draw an ecliptic plane 
color([1, 1, 0, 0.5]) rotate([0,23,0]) { 
    difference() { 
        cylinder(h=.1, r=10.5, center = true);
        cylinder(h=.11, r=10.1, center = true);
    }
}

// drop some taaras on the surface on 10 unit sphere
rotate([0,23,0]) { 
    for (i = [0:360-1]) {
            lat = rands(-90,90,1)[0];
            color(abs(lat)<=10? [0, 1, 0, 1]:[1, 1, 1, 0.5])
            rotate([0,lat,i])
            // rotate([0,rands(-10,10,1)[0],i*2])
            translate([10,0,0])
            sphere(r = abs(lat)<=10?.15:.1);
    }
 }



// Draw a sphere on the ecliptic plane - sun
//for (deg = [0,45, 90]) {

close_to_cardinals = (((deg%90)<=7) || ((deg%90)>=83)) ;
rotate([0,23,0]) {
    translate([10*cos(deg+90), 10*sin(deg+90)])  
    color([1, 1 - (close_to_cardinals ?1:0), 0, 0.5 ])

    sphere(r = 1+((deg%90)==0?0:0));

    %color(close_to_cardinals?[1,0,0,.9]:[1,1,0,0.9]) 
    translate([15, 15, 4]) 
    rotate([90, 0, 180]) 
    linear_extrude(height = .1)
    text( str(nak), size = .5, halign = "center", valign = "center");

    %color([1, 1, 0, 0.9]) 
    translate([15, 15, 1]) 
    rotate([90, 0, 180]) 
    linear_extrude(height = .1)
    text( str(deg, "°,0° ecliptic;"), size = .5, halign = "center", valign = "center");


    
    //scale([0,0,0])
    color([1, 0, 1, 0.5]) 
    //rotate([0,0,deg])
    translate([15, 15, -1]) 
    rotate([90, 26, 180])
    linear_extrude(height = .1)
    text( str( deg, "°,", round(23*sin(deg)), "° equatorial"), size = .5, halign = "center", valign = "center");
}

// drop some 10 random stars on the surface on 10 unit sphere
// for (i = [0:360-1]) {
//  //rands(0,359,3,seed=i);
//     // xs = taras[i];
//     xs =[0,0,0];
//     rotate([xs[0],xs[1],xs[2]]) {
//         rotate([i,23+rands(-10,10,1)[0],0])
//         translate([10,0,0])
//         color([0, 1, 1, 0.5])
//         // scale ( [xs[0]/36, 1,1])
//         sphere(r = .1);
//     }
// }
}





