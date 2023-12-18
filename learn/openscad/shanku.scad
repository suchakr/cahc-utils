
$fn=200;
//use <MCAD/boxes.scad>
$fa=1;
$fs=0.4;
// roundedBox(size=[10,20,30],radius=3,sidesonly=false);

DECL23=23.3;
// DECL = round(sin($t*360)*DECL23);
// ALT = round($t*360);
DA=$t*12*30;
ALT = 360*(DA % 30)/30;
DECL = sin(360*(DA-(DA%30))/(12*30))*DECL23;


//DECL = 23-(DA-(DA%30))/30
MONTHS = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ];
MAASAS = [ "Chaitra", "Baisakhi", "Jyaistha", "Asadha", "Sravana", "Bhadra", "Asvina", "Kartika", "Agrahayana", "Pausa", "Magha", "Phalguna" ];
echo(str($vpr));

/* [Slider] */
// Latitude's slider's value
LAT = 0; // [-30:30]
color("green", 1)  translate([-10,0,-16]) rotate([90,0,90]) linear_extrude(.1) 
text(str([ 
    str("Lat: ", LAT) , str ("Alt: ", ALT), str("Decl:", DECL),
    str(MAASAS[(6+12*(DA-(DA%30))/(12*30))%12]) ,
    str(MONTHS[(8+12*(DA-(DA%30))/(12*30))%12]) ,
]), size=1, halign="left", valign="center");


//sun_paths_by_decl_1(10,LAT, DECL);
rotate([-LAT*1,0,0]) sun_paths_by_decl(1*LAT,DECL,ALT);

module sun_paths_by_decl(lat, decl, alt,sz=10) {

    tp = 1/2;
    /**/
    // color("pink", tp) sunplane(sz,0,0,str("    z+ "));
    rotate ([0,-lat,90]) sunplane(0, 0, 
        ring_radius=sz, ring_color="black", ring_alpha=.2, ring_thickness=.1,
        label="       z+", label_color="red", label_alpha=1);

    // color("green", tp) sunplane(sz,lat,0,str("         eqnx ",""));
    sunplane(0, 0, 
        ring_radius=sz*cos(0), ring_color="green", ring_alpha=0.3, ring_thickness=.2,
        label="eqnx", label_color="", label_alpha=-1);

    // color("cyan",tp) sunplane(sz*cos(DECL23),lat,DECL23,"WinSol");
    sunplane(0, DECL23, 
        ring_radius=sz*cos(DECL23), ring_color="blue", ring_alpha=0.3, ring_thickness=.2,
        label="utryn", label_color="", label_alpha=-1) ;

    // color("cyan", tp) sunplane(sz*cos(DECL23),lat,-DECL23,"SumSol");
    sunplane(0, -DECL23, 
        ring_radius=sz*cos(-DECL23), ring_color="red", ring_alpha=0.3, ring_thickness=.2,
        label="dksnyn", label_color="", label_alpha=-1);
    
    // color("red", tp) sunplane(sz*cos(lat),lat,-lat,"zsd");
    if ( abs(lat) < DECL23 ) {
    sunplane(0, -lat, 
        ring_radius=sz*cos(-lat), ring_color="brown", ring_alpha=.2, ring_thickness=.025,
        label="zsd", label_color="", label_alpha=-1);
    }
    /**/
    // color("yellow", 3*tp) sunplane(sz*cos(lat),lat,decl,"",1); 
    sunplane(0, decl, 
        ring_radius=sz*cos(decl)*1.05, ring_color="yellow", ring_alpha=1, ring_thickness=.4,
        label="", label_color="", label_alpha=-1,
        disk_alt=alt, disk_radius=1, disk_width=.2, disk_color="red", disk_alpha=-1) ;


    // rotate([90,0,90]) translate( [0, -sz*1.3, sz*1.3] ) linear_extrude(.1) 
    // text (str("lat: ", round(lat), " , decl: ", round(decl)), size=1.5, halign="center", font="sans");

    rotate ([lat,0,0]) {
        base(sz);
        directions(sz);
    }
}
module base(sz) { color("black", .3) cylinder(.1,10,sz); }
module sunplane (
    lat, decl, 
    ring_radius=10, ring_color="blue", ring_alpha=0.5, ring_thickness=.3,
    label="", label_color="", label_alpha=-1,
    disk_alt=0, disk_radius=0, disk_width=0, disk_color="", disk_alpha=-1) {
    
    label_color = (len(label_color)==0) ? ring_color : label_color;
    label_alpha = label_alpha <0 ? ring_alpha : label_alpha;

    // disk_color = (len(disk_color)==0) ? ring_color : disk_color;
    // disk_alpha = disk_alpha <0 ? ring_alpha : disk_alpha;


    translate([0,ring_radius*sin(decl),0*-ring_radius*sin(decl/5)]) rotate([0,90+lat,90])  {
     
        difference() {
            color(ring_color, ring_alpha)
            cylinder(ring_thickness,ring_radius,ring_radius, center=true); 
            //translate([0,0,-.025]) 
            cylinder(1.2*ring_thickness,0.98*ring_radius,0.98*ring_radius,center=true); 
        }
        // color("red" )translate([0,sz,0]) 
        if ( disk_radius >0 ){

            rotate([0,0, disk_alt-90]) 
            translate([-1.1*ring_radius,0,0]) 
            //rotate([90,0,90])  
            {
                color(disk_color, disk_alpha) 
                sphere(disk_radius);
            }
            // cylinder(disk_width, disk_radius/2, disk_radius);
            
            //rotate([90,0,90])  
        }

    }

    color(label_color, label_alpha)
    translate ([0,ring_radius*(sin(lat) + sin(decl)),(ring_radius+len(label))]) 
        rotate([90,90,90])
            linear_extrude(.1)
            text(label, size=1, halign="left", valign="center");
}

module sun_paths_by_decl_1(sz,lat, decl) {
    tp = 1/2;
    color("pink", tp) sunplane_1(sz,0,0,str("    z+ "));
    color("green", tp) sunplane_1(sz,lat,0,str("         eqnx ",""));
    color("cyan",tp) sunplane_1(sz*cos(DECL23),lat,DECL23,"WinSol");
    color("cyan", tp) sunplane_1(sz*cos(DECL23),lat,-DECL23,"SumSol");
    color("red", tp) sunplane_1(sz*cos(lat),lat,-lat,"zsd");
    color("yellow", 3*tp) sunplane_1(sz*cos(lat),lat,decl,"",1); 
    directions(sz);
    rotate([90,0,90]) translate( [0, -sz*1.3, sz*1.3] ) linear_extrude(.1) 
    text (str("lat: ", round(lat), " , decl: ", round(decl)), size=1.5, halign="center", font="sans");

    base(sz);
}

module sunplane_1(sz, lat, decl, label, disk=0) {
    sz = (1+1*disk/20)*sz;
    translate([0,sz*sin(decl),0]) rotate([0,90+lat,90])  { 
        difference() {
            cylinder(1,sz,sz); 
            translate([0,0,-.025]) cylinder(1+.05,0.95*sz,0.95*sz); 
        }
        // color("red" )translate([0,sz,0]) 
        if ( disk ==1 ){
            rotate([0,0,ALT]) color("yellow") translate([-1.1*sz,0,0]) rotate([90,90,90])  cylinder(.4, sz/10,sz/5);
        }

    }
    translate ([0,sz*(sin(lat) + sin(decl)),(sz+len(label))]) 
        rotate([90,90,90])
            linear_extrude(.1)
            text(label, size=1, halign="left", valign="center");
}

module directions(sz) {
    translate([0,0,.1]) {
        color("red",.3) rotate([0,90,0]) cylinder(2*sz+5,.1,.1, center=true);
        color("red",.3) rotate([90,0,0]) cylinder(2*sz+5,.1,.1, center=true);
        color("black",.5) rotate([0,0,90]) cylinder(1*sz+5,.1,.05, center=false);
    }


    rotate([0,60,0]) {
        translate( [0,-sz-2.5,0])  text("N",size=2, halign="center");
        translate( [0,sz+2.5,0]) text("s",size=2, halign="center");
    }


    rotate([0,0,-90]) {
        translate( [0,-sz-2.5,0]) text("E",size=2, halign="center");
        translate( [0,sz+2.5,0]) text("W",size=2, halign="center");
    }
}


function rot_xy(t) = [ 
       [ cos(t),  sin(t), 0],
       [ -sin(t), cos(t), 0],
       [       0,  0,    1],
       ];
       
function rot_xz(t) = [
       [ cos(t), 0,  sin(t)],
       [     0,  1,       0],
       [-sin(t), 0,  cos(t)],
];

function rot_yz(t) = [
       [ 1,    0,         0],
       [ 0,  cos(t), -sin(t)],
       [ 0,  sin(t),  cos(t)],
];

function rot_lad(lat,alt,decl,sz=1) = rot_xy(decl)*rot_xz(alt)*rot_yz(lat)*sz;

//echo(rot_lad(90,0,0) * [0,0,1]); //lat [0,-1,0]
//echo(rot_lad(0,90,0) * [0,0,1]); //alt [1,0,0]
//echo(rot_lad(0,0,90) * [0,0,1]); //decl [0,0,1]
//echo(rot_lad(0,0,90) * [-1,0,0]); //decl [0,-1,0]


module ghumao(l,a,d, sz=10) {
    pt = [-1,0,0] ;
    p1 = rot_xz(a) * pt;
    p2 = [p1[0] + 0 , p1[1] + sin(a)*sin(l) , p1[2]*cos(l)];
    p3 = p2+[0, cos(l)*sin(d), -sin(l)*cos(d)];
    rpt = p3*sz;
    echo("****  ", rpt);
    //color ("blue") translate( pt) sphere(sz/20);
    //color ("blue") translate( p1*sz) sphere(sz/20);

    color ("green") translate( rpt) sphere(sz/20);
}

for ( alt = [ 0:30: 180] ) {
    echo(">>>>>>> ", alt);
    //ghumao(0,alt,0);
    //ghumao(0,alt,0);
    ghumao(LAT,alt,DECL);
    //ghumao(45,45,45);
}




