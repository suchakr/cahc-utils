use strict;
use Data::Dumper;
$Data::Dumper::Indent = $Data::Dumper::Sortkeys = 1;

# my $F = '82n.csv';
# open F , "< $F" or die "Unable to open $F";
# my @F =  map { chomp ; [    map {s/\s+/ /g; $_ } split /[,\t]/, $_] } grep {/^\d/ } <F>;
# close F; 

my @F =  map { chomp ; [    map {s/\s+/ /g; $_ } split /[,\t]/, $_] } grep {/^\d/ } <DATA>
my %F1 = () ; $F1{ $_->[2]} = $_  for @F;

my $F = "82taras_of_nakshatras.csv";
open F , "< $F" or die "Unable to open $F";
my @F =  map { chomp ; [    map {s/\s+/ /g; $_ } split /[,\t]/, $_] } grep {/^\d/ } <F>;
close F; 
my %F2 = () ; $F2{ $_->[1]} = $_  for @F;

#warn Dumper \%F1;
#warn Dumper \%F2;

my %tara_info = ();
my %naks_info = ();
for my $n ( keys %F2)  {
  my %info = ();
  @info{qw(seq naks tara name yoga)} =  @ { $F1{$n} };
  @info{qw(oid tara mag ra dec xxx hip ids)} = @ { $F2{$n} };
  my $naks = $info{naks};
  $naks_info{$naks} ||= [];
  push @{ $naks_info{$naks} }, \%info ;
}

my $ttl = 0;
for my $naks ( sort keys %naks_info ) {
    my @taras = 
      map { s/\*\s*//g; $_ } 
      map { ($_->{yoga}?'+':''). $_->{tara}} 
      @{$naks_info{$naks} }  ;
    my @hips = map { $_->{hip}   } @{$naks_info{$naks} }  ;
    my @hips2 = @hips;
    push @hips2 , $hips[0] if @hips == 1;
    my @line_segments = ();
    for my $idx  ( 0 .. -1+$#hips2 ) {
      push @line_segments , ($hips2[$idx] , $hips2[1+$idx]) 
    }
    my ($ast_num, $ast_name) = $naks =~ /^(N\d+).(.*)/;
    my $hips_str = join  qq(| ), map { sprintf '%-10s' , $_ || 'xxx'} map {s/\D//g ; $_ } @hips;
    my $tara_str = join  qq(| ), map { sprintf '%-10s', $_ } @taras;
    my $line_segments_str = join  qq( ), map {$_ || 'xxx'} map {s/\D//g ; $_ } @line_segments;
    $ttl += (0+@hips);
    printf qq(# %s \n) , '-' x 50;  
    printf qq(# %-10s, %3d, %d\n), $naks , 0+@hips , $ttl ;
    printf qq(# %10s | %s \n), $naks , $tara_str;
    printf qq(# %10s | %s \n), $naks , $hips_str;
    printf qq(%s %2d %-44s\n), $ast_num, 0+@line_segments/2, $line_segments_str;
    printf qq(\n);  
}

__DATA__
#	naks	main_id	name	is_yoga	mag	bri	ra	dec
1	N01-Ash	* alf Ari	Hamal	1	2.0	5.0	31.79	23.46
2	N01-Ash	* bet Ari	Sheratan	0	2.7	4.0	28.66	20.81
3	N02-Bha	* 41 Ari	Bharani	1	3.6	3.0	42.50	27.26
4	N02-Bha	* 31 Ari	xxx	0	5.7	1.0	39.16	12.45
5	N02-Bha	* 35 Ari	xxx	0	4.7	2.0	40.86	27.71
6	N03-Kri	* eta Tau	Alcyone	1	2.9	4.0	56.87	24.11
7	N03-Kri	* 17 Tau	Electra	0	3.7	3.0	56.22	24.11
8	N03-Kri	* q Tau	Taygeta	0	4.3	3.0	56.30	24.47
9	N03-Kri	* 20 Tau	Maia	0	3.9	3.0	56.46	24.37
10	N03-Kri	* 23 Tau	Merope	0	4.2	3.0	56.58	23.95
11	N03-Kri	* 27 Tau	Atlas	0	3.6	3.0	57.29	24.05
12	N03-Kri	* 28 Tau	Pleione	0	5.1	2.0	57.30	24.14
13	N04-Roh	* alf Tau	Aldebaran	1	0.9	6.0	68.98	16.51
14	N04-Roh	* gam Tau	Prima Hyadum	0	3.7	3.0	64.95	15.63
15	N04-Roh	* del Tau	Secunda Hyadum	0	3.8	3.0	65.73	17.54
16	N04-Roh	* eps Tau	Ain	0	3.5	3.0	67.15	19.18
17	N04-Roh	* tet02 Tau	Chamukuy	0	3.4	4.0	67.17	15.87
18	N05-Mrg	* gam Ori	Bellatrix	1	1.6	5.0	81.28	6.35
19	N05-Mrg	* phi01 Ori	lambda Ori X-5	0	4.4	3.0	83.71	9.49
20	N05-Mrg	* lam Ori	Heka	0	3.7	3.0	83.78	9.93
21	N06-Ard	* alf Ori	Betelgeuse	1	0.4	7.0	88.79	7.41
22	N07-Pun	* bet Gem	Pollux	1	1.1	6.0	116.33	28.03
23	N07-Pun	* alf Gem	Castor	0	1.6	5.0	113.65	31.89
24	N08-Pus	* del Cnc	Asellus Australis	1	3.9	3.0	131.17	18.15
25	N09-Asl	* del Hya	xxx	0	4.1	3.0	129.41	5.70
26	N09-Asl	* sig Hya	Minchir	0	4.4	3.0	129.69	3.34
27	N09-Asl	* eta Hya	xxx	0	4.3	3.0	130.81	3.40
28	N09-Asl	* eps Hya	Ashlesha	0	3.4	4.0	131.69	6.42
29	N09-Asl	* rho Hya	xxx	0	4.3	3.0	132.11	5.84
30	N09-Asl	* zet Hya	xxx	0	3.1	4.0	133.85	5.95
31	N10-Mag	* alf Leo	Regulus	1	1.4	6.0	152.09	11.97
32	N10-Mag	* eps Leo	xxx	0	3.0	4.0	146.46	23.77
33	N10-Mag	* mu. Leo	Rasalas	0	3.9	3.0	148.19	26.01
34	N10-Mag	* eta Leo	xxx	0	3.4	4.0	151.83	16.76
35	N10-Mag	* zet Leo	Adhafera	0	3.4	4.0	154.17	23.42
36	N10-Mag	* gam Leo	Algieba	0	2.4	5.0	154.99	19.84
37	N11-PPal	* del Leo	Zosma	1	2.5	4.0	168.53	20.52
38	N11-PPal	* tet Leo	Chertan	0	3.4	4.0	168.56	15.43
39	N12-UPal	* bet Leo	Denebola	1	2.1	5.0	177.26	14.57
40	N12-UPal	* 93 Leo	xxx	0	4.5	2.0	177.00	20.22
41	N13-Has	* del Crv	Algorab	1	2.9	4.0	187.47	-16.52
42	N13-Has	* alf Crv	Alchiba	0	4.0	3.0	182.10	-24.73
43	N13-Has	* eps Crv	Minkar	0	3.0	4.0	182.53	-22.62
44	N13-Has	* gam Crv	Gienah	0	2.6	4.0	183.95	-17.54
45	N13-Has	* bet Crv	Kraz	0	2.6	4.0	188.60	-23.40
46	N14-Chi	* alf Vir	Spica	1	1.0	6.0	201.30	-11.16
47	N15-Swa	* alf Boo	Arcturus	1	-0.1	7.0	213.92	19.18
48	N16-Vis	* alf02 Lib	Zubenelgenubi	1	2.8	4.0	222.72	-16.04
49	N17-Anu	* del Sco	Dschubba	1	2.3	5.0	240.08	-22.62
50	N17-Anu	* pi. Sco	Fang	0	2.9	4.0	239.71	-26.11
51	N17-Anu	* bet Sco	Acrab	0	2.5	4.0	241.36	-19.81
52	N17-Anu	* ome Sco	xxx	0	4.0	3.0	241.70	-20.67
53	N18-Jye	* alf Sco	Antares	1	0.9	6.0	247.35	-26.43
54	N19-Mul	* lam Sco	Shaula	1	1.6	5.0	263.40	-37.10
55	N19-Mul	* tet Sco	Sargas	0	1.9	5.0	264.33	-43.00
56	N20-PAsh	* eps Sgr	Kaus Australis	1	1.9	5.0	276.04	-34.38
57	N20-PAsh	* gam02 Sgr	Alnasl	0	3.0	4.0	271.45	-30.42
58	N20-PAsh	* del Sgr	Kaus Media	0	2.7	4.0	275.25	-29.83
59	N20-PAsh	* lam Sgr	Kaus Borealis	0	2.8	4.0	276.99	-25.42
60	N21-UAsh	* sig Sgr	Nunki	1	2.1	5.0	283.82	-26.30
61	N21-UAsh	* phi Sgr	xxx	0	3.1	4.0	281.41	-26.99
62	N21-UAsh	* zet Sgr	Ascella	0	2.6	4.0	285.65	-29.88
63	N21-UAsh	* tau Sgr	xxx	0	3.3	4.0	286.74	-27.67
64	N22-Shr	* alf Aql	Altair	1	0.8	6.0	297.70	8.87
65	N22-Shr	* gam Aql	Tarazed	0	2.7	4.0	296.56	10.61
66	N22-Shr	* bet Aql	Alshain	0	3.7	3.0	298.83	6.41
67	N23-Dha	* alf Del	Sualocin	1	3.8	3.0	309.91	15.91
68	N23-Dha	* eps Del	Aldulfin	0	4.0	3.0	308.30	11.30
69	N23-Dha	* bet Del	Rotanev	0	3.6	3.0	309.39	14.60
70	N23-Dha	* del Del	xxx	0	4.4	3.0	310.86	15.07
71	N23-Dha	* gam Del	xxx	0	3.9	3.0	311.66	16.12
72	N24-Sha	* gam Aqr	Sadachbia	1	3.8	3.0	335.41	-1.39
73	N24-Sha	* kap Aqr	Situla	0	5.0	2.0	339.44	-4.23
74	N24-Sha	* lam Aqr	xxx	0	3.8	3.0	343.15	-7.58
75	N25-PBha	* alf Peg	Markab	1	2.5	5.0	346.19	15.21
76	N25-PBha	* bet Peg	Scheat	0	2.4	5.0	345.94	28.08
77	N26-UBha	* alf And	Alpheratz	1	2.1	5.0	2.10	29.09
78	N26-UBha	* gam Peg	Algenib	0	2.8	4.0	3.31	15.18
79	N27-Rev	* alf Psc	Alrescha	1	3.8	3.0	30.51	2.76
80	N28-Abh	* alf Lyr	Vega	1	0.0	7.0	279.23	38.78
81	N28-Abh	* eps01 Lyr	xxx	0	4.7	2.0	281.08	39.67
82	N28-Abh	* zet01 Lyr	xxx	0	4.4	3.0	281.19	37.61