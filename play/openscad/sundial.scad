$fa=1;
$fs=.4;
//$fn=100;


module concentrics(base_height=0.5, base_radius) {
    step = 0.05;
    x=[for(i=[1:1:12]) each([
        [i, 0] , [i,-step] , [i+step, -step] , [i+step,0]
    ]) ];
    
    color("brown")
    translate([0,0,1.1*base_height])
    rotate_extrude(angle=360, convexity=2, $fn=24)
    polygon(points=x);
}


module radials (base_height=0.5, base_radius) {
    for(x=[0:-15:-180]) {
        //rot = atan(tan(x)/sin(lat));
        color("blue")
        translate([0,0,base_height])
        rotate([x,90,180])
        cylinder(base_radius * .75, .15,.15); 
    
        color("red")
        translate( [base_radius*.82*sin(x-90),base_radius*.8*cos(x-90),1*base_height] )
        rotate([0,0,0])
        linear_extrude(1/10)
        text(str( x==0?"E ":"" , 18+(x/15), x==-180?" W":"" ), size=.8, halign="center", valign="center");
        if(x==0) { }
    
}
}

module dial(base_height=1.5, base_radius=16, tilt=12, scalexy=1) {
    scale([scalexy,scalexy,1])
    translate ([0,0,scalexy*base_radius*sin(tilt)])
    rotate([tilt,0,0])
    union () {
        difference() {
            union () {
                cylinder(h=base_height, r1=base_radius*1,r2=base_radius*.90, $fn=24); 
                radials(base_height, base_radius);
                concentrics(base_height, base_radius);
             }
             cylinder(h=scalexy*base_radius*2/sin(tilt) , r=1.1, center=true);
     
        }
        translate([0,0,-scalexy*base_radius/tan(90-tilt)])
        color("red") cylinder(h=base_radius*0.55 + scalexy*base_radius/tan(90-tilt) , r=1.1, center=!true);
    }
}


for ( alt=[10:10:40] ) {
translate ([20*(alt)/5,0,0])
dial(base_height=1.5, base_radius=16, tilt=90-alt, scalexy=1);
}






module needle() {
    color("olive")
    translate([0,0,base_height])
    cylinder(h=10, r1=1, r2=.5);
}

 




