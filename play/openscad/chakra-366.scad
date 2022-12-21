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

module daily_radials (base_height=0.5, base_radius) {
    rotate([0,0,270])
    for(y=[1:(1*366/366):366]) {
        x = (y-1)*360/366;
        m10 = (y-1)%10==0;
        //rot = atan(tan(x)/sin(lat));
        color("blue")
        translate([0,0,base_height])
        rotate([x,90,180])
        cylinder(base_radius * 1, .01 *(m10?3:1) ,.01*(m10?3:1)); 
    
        if (m10) {
            color("maroon")
            translate( [base_radius*1.05*sin(x-90),base_radius*1.05*cos(x-90),1*base_height] )
            rotate([0,0,90])
            linear_extrude(1/10)
            text(str( round(y-1)), size=.35, halign="center", valign="center");
        }
        // color("maroon")
        // translate( [base_radius*1.05*sin(x-90),base_radius*1.05*cos(x-90),1*base_height] )
        // rotate([0,0,90])
        // linear_extrude(1/10)
        // text(str( round(y-1)), size=.35, halign="center", valign="center");
    
    }
}

module seasonal_radials (base_height=0.5, base_radius) {
    rotate([0,0,270])
    for(y=[1:(366/6):366]) {
        x = (y-1)*360/366;
        //rot = atan(tan(x)/sin(lat));
        color("blue")
        translate([0,0,base_height])
        rotate([x,90,180])
        cylinder(base_radius * 1.05, .005,.055); 
    
        color("maroon")
        translate( [base_radius*1.1*sin(x-90),base_radius*1.1*cos(x-90),1*base_height] )
        rotate([0,0,90])
        linear_extrude(1/10)
        text(str( round(y-1)), size=0.75, halign="center", valign="center");
        // text(str( x==0?"E ":"" , 18+(x/15), x==-180?" W":"" ), size=.5, halign="center", valign="center");
    
    }
}

module dial(base_height=1.5, base_radius=16, tilt=12, scalexy=1) {
    scale([scalexy,scalexy,1])
    translate ([0,0,scalexy*base_radius*sin(tilt)])
    // rotate([tilt,0,0])
    union () {
        difference() {
            union () {
                cylinder(h=base_height, r1=base_radius*1,r2=base_radius*1, $fn=366); 
                daily_radials(base_height, base_radius);
                // concentrics(base_height, base_radius);
             }
             cylinder(h=scalexy*base_radius*2/sin(tilt) , r=base_radius*.90, center=true);
     
        }
        seasonal_radials(base_height, base_radius);
        *translate([0,0,-scalexy*base_radius/tan(90-tilt)])
        color("red") cylinder(h=base_radius*0.55 + scalexy*base_radius/tan(90-tilt) , r=1.1, center=!true);
    }
}

module seasonal_radials2d (base_height=0.5, base_radius) {
    rotate([0,0,-90]) 
    {
        for(y=[1:(366/6):367]) {
            x = (y-1)*360/366;
            rotate([0,0,x+90])
            polygon(points=[[-.25,0],[.25,0], [.25,1.2*base_radius ], [-.25,1.2*base_radius ]]);
        } 
        
        for(y=[1:10:367]) {
            x = (y-1)*360/366;
            rotate([0,0,x+90])
            polygon(points=[[-.1,0 +base_radius],[.1,0+base_radius], [.1,1.1*base_radius ], [-.1,1.1*base_radius ]]);
        } 
        
        for(y=[1:(366/6):367]) { 
            x = (y-1)*360/366;
            color("red")
            translate( [base_radius*1.25*sin(x-90)*(y>366?1.1:1),base_radius*1.25*cos(x-90),0*base_height*(y>366?1.1:1)] )
            rotate([0,0,90-x])
            text(str( round(y-1)), size=1.95, halign="center", valign="center");
        }

        for(y=[1:10:367]) {
            x = (y-1)*360/366;
            rotate([0,0,2])
            color("red")
            translate( [base_radius*1.13*sin(x-90)*(y>366?1.1:1),base_radius*1.13*cos(x-90),0*base_height*(y>366?1.1:1)] )
            rotate([0,0,90-x])
            text(str( round(y-1)), size=.95, halign="right", valign="center");
        } 
    }
}

module dial2d(base_height=1.5, base_radius=26, tilt=12, scalexy=1) {
    // scale([scalexy,scalexy,0])
    // translate ([0,0,scalexy*base_radius*sin(tilt*0)])
    // rotate([tilt,0,0])
    union () {
        difference() {
            union () {
                circle (base_radius*1, $fn=366); 
                // seasonal_radials2d(base_height, base_radius);
                // concentrics(base_height, base_radius);
             }
             circle(base_radius*.90);
        }
        seasonal_radials2d(base_height, base_radius);
        // seasonal_radials(base_height, base_radius);
        // *translate([0,0,-scalexy*base_radius/tan(90-tilt)])
        // color("red") cylinder(h=base_radius*0.55 + scalexy*base_radius/tan(90-tilt) , r=1.1, center=!true);
    }
}

for ( alt=[10:40:40] ) {
    // translate ([20*(alt-10)/5,0,0])
    dial2d(); 
    // projection()
    // dial(base_height=1.5, base_radius=16, tilt=90-alt, scalexy=4);
}

// rotate([0,0,-60])polygon(points=[[-.5,0],[.5,0], [0,30-5]]);



 




