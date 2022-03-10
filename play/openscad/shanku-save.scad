
$fn=90;
DECL23=23.3;
// DECL = round(sin($t*360)*DECL23);
// ALT = round($t*360);
DA=round($t*46*30);
ALT = 360*(DA % 30)/30;
DECL = sin(360*DA/(46*30))*DECL23;
//DECL = 23-(DA-(DA%30))/30


// color("red", 1)linear_extrude(.1) text(str([$t, DA, DECL, ALT]), size=4, halign="left", valign="center");

LAT = 12;

// sun_paths_by_decl_1(10,LAT, DECL);
rotate([-LAT,0,0]) sun_paths_by_decl(LAT,DECL,ALT);

module sun_paths_by_decl(lat, decl, alt,sz=10) {

    tp = 1/2;
    // color("pink", tp) sunplane(sz,0,0,str("    z+ "));
    rotate ([0,-lat,90]) sunplane(0, 0, 
        ring_radius=sz, ring_color="black", ring_alpha=.3, ring_thickness=.1,
        label="       z+", label_color="red", label_alpha=1);

    // color("green", tp) sunplane(sz,lat,0,str("         eqnx ",""));
    sunplane(0, 0, 
        ring_radius=sz*cos(0), ring_color="green", ring_alpha=0.5, ring_thickness=.2,
        label="eqnx", label_color="", label_alpha=-1);

    // color("cyan",tp) sunplane(sz*cos(DECL23),lat,DECL23,"WinSol");
    sunplane(0, DECL23, 
        ring_radius=sz*cos(DECL23), ring_color="blue", ring_alpha=0.5, ring_thickness=.2,
        label="daks", label_color="", label_alpha=-1) ;

    // color("cyan", tp) sunplane(sz*cos(DECL23),lat,-DECL23,"SumSol");
    sunplane(0, -DECL23, 
        ring_radius=sz*cos(-DECL23), ring_color="red", ring_alpha=0.5, ring_thickness=.2,
        label="utta", label_color="", label_alpha=-1);
    
    // color("red", tp) sunplane(sz*cos(lat),lat,-lat,"zsd");
    sunplane(0, -lat, 
        ring_radius=sz*cos(-lat), ring_color="brown", ring_alpha=1, ring_thickness=.025,
        label="zsd", label_color="", label_alpha=-1);

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

    color(ring_color, ring_alpha)
    translate([0,ring_radius*sin(decl),0*-ring_radius*sin(decl/5)]) rotate([0,90+lat,90])  {
     
        difference() {
            cylinder(ring_thickness,ring_radius,ring_radius, center=true); 
            // translate([0,0,-.025]) 
            cylinder(1.2*ring_thickness,0.98*ring_radius,0.98*ring_radius,center=true); 
        }
        // color("red" )translate([0,sz,0]) 
        if ( disk_radius >0 ){
            rotate([0,0, disk_alt-90]) 
            color(disk_color, disk_alpha) 
            translate([-1.1*ring_radius,0,0]) 
            rotate([90,0,90])  
            sphere(disk_radius);
            // cylinder(disk_width, disk_radius/2, disk_radius);
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
        color("red") rotate([0,90,0]) cylinder(2*sz+5,.1,.1, center=true);
        color("red") rotate([90,0,0]) cylinder(2*sz+5,.1,.1, center=true);
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




