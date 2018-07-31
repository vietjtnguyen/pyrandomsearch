import unittest

from . import cli


class TestSimpleNominalBehavior(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_min_2d_quadratic(self):
        cli.check_output(
            self, 'pyrandomsearch.pyrandomsearch',
            [
                '--rng-seed=0',
                'python -c "print(({})**2+({})**2)"',
            ],
            '''\
# score x y
## this is a comment
32 4 4
''',
            '''\
## Existing points:
32.0 4.0 4.0
## New points:
30.8396661335 4.559075211394427 3.170883055290584
26.8688369961 3.6810440410421053 3.649486506897164
20.0085790318 2.683552227074067 3.578704580766603
15.1431822194 2.8943224323890955 2.601168944305476
11.1792344223 1.9051141811224097 2.747685276589304
12.3725091753 2.7430295562795797 2.2018851079605106
16.807880024 1.7064026330221667 3.7277432956124663
5.65452379843 1.16916878643369 2.070644379717878
6.40226203589 2.012641359427187 1.5334721367568984
3.66990154648 1.5385620793664883 1.1413712255074144
5.65614449004 1.1695755912864665 2.0708059847102174
5.79087243577 2.3432671674336083 0.5476964650207583
2.03731017698 0.5538411961814022 1.315511347877832
3.08048786841 -0.3618344505110467 1.717429386853897
2.61612310614 1.4081547268968233 0.7957533356870131
2.31990004083 -0.43574376683307003 1.4594613425830965
5.58964634677 0.4879638084314266 2.3133390733812074
1.18852532315 -0.39970897767577496 1.0142771102205774
0.347863891499 -0.5889126125099573 0.03233923817085682
0.756507367779 -0.1357902015877146 -0.8591090669596281
## Best point: 0.347863891499 -0.5889126125099573 0.03233923817085682
''')

    def test_max_3d_quadratic(self):
        cli.check_output(
            self, 'pyrandomsearch.pyrandomsearch',
            [
                '--rng-seed=0',
                '--optimization-type=max',
                'python -c "print(-({})**2-({})**2-({})**2)"',
            ],
            '''\
# score x y
## this is a comment
-48 4 4 4
''',
            '''\
## Existing points:
-48.0 4.0 4.0 4.0
## New points:
-44.0029339764 4.518454613304797 3.231124013025664 3.625788120716066
-41.5508443545 4.860191844851102 2.293685651053998 3.5592675819408393
-35.2543400755 4.974994983351488 1.7612377232552234 2.7206261546471167
-37.8424132057 5.136415571253578 2.5881644286018877 2.1819837706984946
-35.9355250875 4.786452736822589 2.691140098843744 2.404820212415717
-34.5354344823 4.797471047215281 2.5913129852907244 2.191986096142842
-33.1400103088 5.153471710868205 1.6957313222150088 1.9251584134687738
-41.7087416887 5.857250556464365 2.2674092086461686 1.503400508199722
-27.237387763 4.814843775894327 1.7556150019879595 0.9861455985657087
-32.1642939144 5.0220338773955575 2.591390528075396 0.4776659708192481
-19.1122357787 3.827005315419914 1.8993109416693599 0.9267599696086954
-27.3452483784 4.82268976231587 1.8108181861412487 0.8988043900487119
-16.8333279679 3.6696128109062327 1.0824679613841908 1.4817330726341966
-13.7715759113 2.9192725396957693 1.7435027157710667 1.486479744361911
-13.3186906654 3.3440162388478507 1.277320606021691 0.7104210928540321
-21.0614642589 4.155856824065753 1.4886162074244615 1.2547271033122067
-17.5091724753 3.414826486583844 2.2655939716470366 0.84570473418261
-11.127116981 2.5831748421801524 1.8451112514942438 1.0246410031566862
-7.99957060959 1.6629208781692455 1.799159319280752 1.4132552870527617
-7.67002198246 2.1997169166217474 1.5717310449936432 0.6007736607026715
-8.7531467298 2.4697944382328254 0.9418380365446644 1.3289858071459397
-4.29178460964 1.9280910988116005 0.7515177349760452 0.09731607443651447
-1.94929457236 1.2691162935876275 0.29584665427214696 -0.5011119264877136
-1.04825432763 0.7612966782288914 0.6160333869360775 0.29863784342966626
-0.00143169264485 0.03273733544301849 -0.008380984032275496 0.017021122747791495
-0.968683275645 0.06387361536123298 0.03935453682695431 -0.9813534823585046
-1.07263213691 0.6769094301736259 -0.3449003158876072 0.7038959669938321
## Best point: -0.00143169264485 0.03273733544301849 -0.008380984032275496 0.017021122747791495
''')