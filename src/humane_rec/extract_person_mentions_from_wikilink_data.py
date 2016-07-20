#!/usr/bin/env python
'''
| Filename    : tmp.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Wed Jul 20 01:25:43 2016 (-0400)
| Last-Updated: Wed Jul 20 02:59:10 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 22
'''
from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TFileObjectTransport
from bisect import bisect_left
import io
import sys
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument(
    '--thrift_class_dir', default='data/wiki_link', type=str)
arg_parser.add_argument('--thrift_data_dir', default='data', type=str)
arg_parser.add_argument(
    '--out_fn', default='data/wiki_link_individual_mentions', type=str)
args = arg_parser.parse_args()
sys.path.append(args.thrift_class_dir)
from edu.umass.cs.iesl.wikilink.expanded.data.constants import WikiLinkItem

pp = WikiLinkItem()
pool = set('''
http://en.wikipedia.org/wiki/A._Alfred_Taubman
http://en.wikipedia.org/wiki/A._Elizabeth_Jones
http://en.wikipedia.org/wiki/Abdel_Aziz_al-Rantissi
http://en.wikipedia.org/wiki/Abdul_Aziz_al-Hakim
http://en.wikipedia.org/wiki/Abigail_(name)
http://en.wikipedia.org/wiki/Abraham_Lincoln
http://en.wikipedia.org/wiki/Addison_(name)
http://en.wikipedia.org/wiki/Ahmad
http://en.wikipedia.org/wiki/Ahmed_Chalabi
http://en.wikipedia.org/wiki/Al_Gore
http://en.wikipedia.org/wiki/Al_Sharpton
http://en.wikipedia.org/wiki/Alan_Greenspan
http://en.wikipedia.org/wiki/Alana_Stewart
http://en.wikipedia.org/wiki/Alessio_Vinci
http://en.wikipedia.org/wiki/Alexander
http://en.wikipedia.org/wiki/Alice_(given_name)
http://en.wikipedia.org/wiki/Allan_Chernoff
http://en.wikipedia.org/wiki/Amara_Essy
http://en.wikipedia.org/wiki/Andrea_Yates
http://en.wikipedia.org/wiki/Andrew_Jackson
http://en.wikipedia.org/wiki/Andy_(given_name)
http://en.wikipedia.org/wiki/Anna_(name)
http://en.wikipedia.org/wiki/Anne_Desclos
http://en.wikipedia.org/wiki/Antasari_Azhar
http://en.wikipedia.org/wiki/Anwar_Ibrahim
http://en.wikipedia.org/wiki/Ari_Fleischer
http://en.wikipedia.org/wiki/Arnold_Schwarzenegger
http://en.wikipedia.org/wiki/Asa_Hutchinson
http://en.wikipedia.org/wiki/Ashley_(name)
http://en.wikipedia.org/wiki/Ashley_Olsen
http://en.wikipedia.org/wiki/Barack_Obama
http://en.wikipedia.org/wiki/Barbara_(given_name)
http://en.wikipedia.org/wiki/Barbara_Boxer
http://en.wikipedia.org/wiki/Barry_Diller
http://en.wikipedia.org/wiki/Barry_Goldwater
http://en.wikipedia.org/wiki/Barry_Manilow
http://en.wikipedia.org/wiki/Ben_Wedeman
http://en.wikipedia.org/wiki/Benjamin_Franklin
http://en.wikipedia.org/wiki/Bernard
http://en.wikipedia.org/wiki/Bernard_Francis_Law
http://en.wikipedia.org/wiki/Bernard_Lewis
http://en.wikipedia.org/wiki/Bernie_Sanders
http://en.wikipedia.org/wiki/Bill_Clinton
http://en.wikipedia.org/wiki/Bill_Gates
http://en.wikipedia.org/wiki/Bill_Richardson
http://en.wikipedia.org/wiki/Bill_Schneider_(journalist)
http://en.wikipedia.org/wiki/Bill_Tucker
http://en.wikipedia.org/wiki/Bob_Dornan
http://en.wikipedia.org/wiki/Bob_Graham
http://en.wikipedia.org/wiki/Bobbie_Jo_Stinnett
http://en.wikipedia.org/wiki/Brent_Sadler
http://en.wikipedia.org/wiki/Brian
http://en.wikipedia.org/wiki/Brian_Williams
http://en.wikipedia.org/wiki/Britt_Ekland
http://en.wikipedia.org/wiki/Bruce_Babbitt
http://en.wikipedia.org/wiki/Callum_McCarthy
http://en.wikipedia.org/wiki/Candy_Crowley
http://en.wikipedia.org/wiki/Carl_(name)
http://en.wikipedia.org/wiki/Carl_Icahn
http://en.wikipedia.org/wiki/Carl_Levin
http://en.wikipedia.org/wiki/Carly_Fiorina
http://en.wikipedia.org/wiki/Carol_Moseley_Braun
http://en.wikipedia.org/wiki/Carrot_Top
http://en.wikipedia.org/wiki/Chad_(given_name)
http://en.wikipedia.org/wiki/Chad_Myers
http://en.wikipedia.org/wiki/Charles,_Prince_of_Wales
http://en.wikipedia.org/wiki/Charles_B._Rangel
http://en.wikipedia.org/wiki/Charlie_Crist
http://en.wikipedia.org/wiki/Chris_Dodd
http://en.wikipedia.org/wiki/Chris_Matthews
http://en.wikipedia.org/wiki/Chris_Rix
http://en.wikipedia.org/wiki/Christina
http://en.wikipedia.org/wiki/Christine_(name)
http://en.wikipedia.org/wiki/Christine_Todd_Whitman
http://en.wikipedia.org/wiki/Christopher_Hitchens
http://en.wikipedia.org/wiki/Christopher_Reeve
http://en.wikipedia.org/wiki/Chuck_Hagel
http://en.wikipedia.org/wiki/Chuck_Robb
http://en.wikipedia.org/wiki/Claudia_Kennedy
http://en.wikipedia.org/wiki/Colin_Powell
http://en.wikipedia.org/wiki/Condoleezza_Rice
http://en.wikipedia.org/wiki/Corey_Feldman
http://en.wikipedia.org/wiki/Crystal_(given_name)
http://en.wikipedia.org/wiki/Curt_Weldon
http://en.wikipedia.org/wiki/Dale_Bumpers
http://en.wikipedia.org/wiki/Dan_Glickman
http://en.wikipedia.org/wiki/Dan_Rather
http://en.wikipedia.org/wiki/Daniel_Pearl
http://en.wikipedia.org/wiki/Daryn_Kagan
http://en.wikipedia.org/wiki/Dave_(given_name)
http://en.wikipedia.org/wiki/David_Cobb
http://en.wikipedia.org/wiki/David_Frum
http://en.wikipedia.org/wiki/Debbie
http://en.wikipedia.org/wiki/Denise_(given_name)
http://en.wikipedia.org/wiki/Dennis_Hastert
http://en.wikipedia.org/wiki/Dennis_Kozlowski
http://en.wikipedia.org/wiki/Dennis_Kucinich
http://en.wikipedia.org/wiki/Dennis_Rader
http://en.wikipedia.org/wiki/Dianne_Feinstein
http://en.wikipedia.org/wiki/Dick_Cheney
http://en.wikipedia.org/wiki/Digvijay_Singh_(politician)
http://en.wikipedia.org/wiki/Dominique_de_Villepin
http://en.wikipedia.org/wiki/Donald
http://en.wikipedia.org/wiki/Donald_J._Carty
http://en.wikipedia.org/wiki/Donald_Rumsfeld
http://en.wikipedia.org/wiki/Donna_Hanover
http://en.wikipedia.org/wiki/Douglas_Wilder
http://en.wikipedia.org/wiki/Duane_Chapman
http://en.wikipedia.org/wiki/Dubya#George_Walker_Bush
http://en.wikipedia.org/wiki/Duke_Cunningham
http://en.wikipedia.org/wiki/Dwight_Clinton_Jones
http://en.wikipedia.org/wiki/Edward
http://en.wikipedia.org/wiki/Edward_H._Brooks
http://en.wikipedia.org/wiki/Ehud_Barak
http://en.wikipedia.org/wiki/Eliot_Spitzer
http://en.wikipedia.org/wiki/Elizabeth_(given_name)
http://en.wikipedia.org/wiki/Elizabeth_Dole
http://en.wikipedia.org/wiki/Elizabeth_Smart
http://en.wikipedia.org/wiki/Eric_Robert_Rudolph
http://en.wikipedia.org/wiki/Ernie_Pyle
http://en.wikipedia.org/wiki/Errol_Flynn
http://en.wikipedia.org/wiki/Fabian_(name)
http://en.wikipedia.org/wiki/Federico_Peña
http://en.wikipedia.org/wiki/Felicia
http://en.wikipedia.org/wiki/Francis_Fukuyama
http://en.wikipedia.org/wiki/Frank_Keating
http://en.wikipedia.org/wiki/Franklin_D._Roosevelt
http://en.wikipedia.org/wiki/François_Bozizé
http://en.wikipedia.org/wiki/Freddy_(given_name)
http://en.wikipedia.org/wiki/Frederick_Chiluba
http://en.wikipedia.org/wiki/Frederick_W._Smith
http://en.wikipedia.org/wiki/Fredricka_Whitfield
http://en.wikipedia.org/wiki/Fu_Ying
http://en.wikipedia.org/wiki/Gary_(given_name)
http://en.wikipedia.org/wiki/Geoff_Hoon
http://en.wikipedia.org/wiki/George_Allen_(U.S._politician)
http://en.wikipedia.org/wiki/George_Carlin
http://en.wikipedia.org/wiki/George_Lucas
http://en.wikipedia.org/wiki/George_McGovern
http://en.wikipedia.org/wiki/George_Tenet
http://en.wikipedia.org/wiki/George_W._Bush
http://en.wikipedia.org/wiki/Geraldine_Ferraro
http://en.wikipedia.org/wiki/Geraldo_Rivera
http://en.wikipedia.org/wiki/Gerhard_Schröder
http://en.wikipedia.org/wiki/Gholamhossein_Karbaschi
http://en.wikipedia.org/wiki/Given_name
http://en.wikipedia.org/wiki/Gloria_Allred
http://en.wikipedia.org/wiki/Gloria_Macapagal-Arroyo
http://en.wikipedia.org/wiki/Gordon_Campbell_(Canadian_politician)
http://en.wikipedia.org/wiki/Guy_Verhofstadt
http://en.wikipedia.org/wiki/Harrison_Ford
http://en.wikipedia.org/wiki/Harry_(name)
http://en.wikipedia.org/wiki/Heidi_Collins
http://en.wikipedia.org/wiki/Heidi_Fleiss
http://en.wikipedia.org/wiki/Henry_Cisneros
http://en.wikipedia.org/wiki/Hilary_(name)
http://en.wikipedia.org/wiki/Hilary_Duff
http://en.wikipedia.org/wiki/Hillary_Rodham_Clinton
http://en.wikipedia.org/wiki/Horatio_Seymour
http://en.wikipedia.org/wiki/Howard_Dean
http://en.wikipedia.org/wiki/Howell_(surname)
http://en.wikipedia.org/wiki/Hu_Jintao
http://en.wikipedia.org/wiki/Hugh_Hefner
http://en.wikipedia.org/wiki/Igor_Ivanov
http://en.wikipedia.org/wiki/Isaac_Asimov
http://en.wikipedia.org/wiki/J._D._Hayworth
http://en.wikipedia.org/wiki/Jack_(name)
http://en.wikipedia.org/wiki/Jack_Cafferty
http://en.wikipedia.org/wiki/Jack_Straw
http://en.wikipedia.org/wiki/Jack_Welch
http://en.wikipedia.org/wiki/James_(name)
http://en.wikipedia.org/wiki/James_A._Kelly
http://en.wikipedia.org/wiki/James_Baker
http://en.wikipedia.org/wiki/James_Carville
http://en.wikipedia.org/wiki/Jamie_McIntyre
http://en.wikipedia.org/wiki/Jane_(given_name)
http://en.wikipedia.org/wiki/Jane_Arraf
http://en.wikipedia.org/wiki/Jane_Fonda
http://en.wikipedia.org/wiki/Javier_Solana
http://en.wikipedia.org/wiki/Jay_Garner
http://en.wikipedia.org/wiki/Jean-Marc_de_La_Sablière
http://en.wikipedia.org/wiki/Jeanne_(given_name)
http://en.wikipedia.org/wiki/Jeb_Bush
http://en.wikipedia.org/wiki/Jeff_Greenfield
http://en.wikipedia.org/wiki/Jeffrey_(name)
http://en.wikipedia.org/wiki/Jennifer_Tilly
http://en.wikipedia.org/wiki/Jeremy_Greenstock
http://en.wikipedia.org/wiki/Jerry_Brown
http://en.wikipedia.org/wiki/Jesse_Ventura
http://en.wikipedia.org/wiki/Jessica_Lynch
http://en.wikipedia.org/wiki/Jim_Cramer
http://en.wikipedia.org/wiki/Jim_McGreevey
http://en.wikipedia.org/wiki/Jim_McMahon
http://en.wikipedia.org/wiki/Jimmy_Carter
http://en.wikipedia.org/wiki/Jimmy_Doolittle
http://en.wikipedia.org/wiki/Joan_(given_name)
http://en.wikipedia.org/wiki/Joe_Biden
http://en.wikipedia.org/wiki/John_(given_name)
http://en.wikipedia.org/wiki/John_Ashcroft
http://en.wikipedia.org/wiki/John_Bell_(Tennessee_politician)
http://en.wikipedia.org/wiki/John_C._Breckinridge
http://en.wikipedia.org/wiki/John_Edwards
http://en.wikipedia.org/wiki/John_F._Kennedy
http://en.wikipedia.org/wiki/John_George_Nicolay
http://en.wikipedia.org/wiki/John_Howard
http://en.wikipedia.org/wiki/John_K._Davis
http://en.wikipedia.org/wiki/John_Kerry
http://en.wikipedia.org/wiki/John_King_(journalist)
http://en.wikipedia.org/wiki/John_McCain
http://en.wikipedia.org/wiki/John_Negroponte
http://en.wikipedia.org/wiki/John_T._Casteen_III
http://en.wikipedia.org/wiki/John_Wayne
http://en.wikipedia.org/wiki/Joschka_Fischer
http://en.wikipedia.org/wiki/Joseph_(name)
http://en.wikipedia.org/wiki/Joseph_Hazelwood
http://en.wikipedia.org/wiki/Joshua_(name)
http://en.wikipedia.org/wiki/José_María_Aznar
http://en.wikipedia.org/wiki/Joy_(given_name)
http://en.wikipedia.org/wiki/Joyce_(name)
http://en.wikipedia.org/wiki/João_Bosco_Mota_Amaral
http://en.wikipedia.org/wiki/Judith_Giuliani
http://en.wikipedia.org/wiki/Judy_Woodruff
http://en.wikipedia.org/wiki/Justice_and_Development_Party_(Turkey)
http://en.wikipedia.org/wiki/Juwono_Sudarsono
http://en.wikipedia.org/wiki/Karl_Rove
http://en.wikipedia.org/wiki/Kate_(given_name)
http://en.wikipedia.org/wiki/Katherine_(given_name)
http://en.wikipedia.org/wiki/Kathie_Lee_Gifford
http://en.wikipedia.org/wiki/Katrina_Leung
http://en.wikipedia.org/wiki/Kelli_Arena
http://en.wikipedia.org/wiki/Kelly_Wallace
http://en.wikipedia.org/wiki/Ken_(name)
http://en.wikipedia.org/wiki/Kenneth_Lay
http://en.wikipedia.org/wiki/Kenneth_Starr
http://en.wikipedia.org/wiki/Kevin_Sites
http://en.wikipedia.org/wiki/Kim_Kye_Gwan
http://en.wikipedia.org/wiki/Kira_(given_name)
http://en.wikipedia.org/wiki/Kobe_Bryant
http://en.wikipedia.org/wiki/Kyra_Phillips
http://en.wikipedia.org/wiki/L._Paul_Bremer
http://en.wikipedia.org/wiki/Larry
http://en.wikipedia.org/wiki/Larry_Ellison
http://en.wikipedia.org/wiki/Larry_King
http://en.wikipedia.org/wiki/Larry_Klayman
http://en.wikipedia.org/wiki/Larry_Parr_(chess_player)
http://en.wikipedia.org/wiki/Larry_Sabato
http://en.wikipedia.org/wiki/Laurence_Foley
http://en.wikipedia.org/wiki/Lawrence_Summers
http://en.wikipedia.org/wiki/Leon_(given_name)
http://en.wikipedia.org/wiki/Leon_Klinghoffer
http://en.wikipedia.org/wiki/Les_Aspin
http://en.wikipedia.org/wiki/Leslie_L._Byrne
http://en.wikipedia.org/wiki/Lester_Maddox
http://en.wikipedia.org/wiki/Liam
http://en.wikipedia.org/wiki/Liz_George
http://en.wikipedia.org/wiki/Lloyd_Bentsen
http://en.wikipedia.org/wiki/Lou_Dobbs
http://en.wikipedia.org/wiki/Lyndon_B._Johnson
http://en.wikipedia.org/wiki/Marco_(given_name)
http://en.wikipedia.org/wiki/Margaret_Hassan
http://en.wikipedia.org/wiki/Mark_(given_name)
http://en.wikipedia.org/wiki/Mark_Alan_Wilson
http://en.wikipedia.org/wiki/Mark_Cuban
http://en.wikipedia.org/wiki/Mark_Warner
http://en.wikipedia.org/wiki/Martha_Stewart
http://en.wikipedia.org/wiki/Martin_(name)
http://en.wikipedia.org/wiki/Martin_Savidge
http://en.wikipedia.org/wiki/Marvin_Davis
http://en.wikipedia.org/wiki/Mary_(given_name)
http://en.wikipedia.org/wiki/Massoud_Barzani
http://en.wikipedia.org/wiki/Matt_Drudge
http://en.wikipedia.org/wiki/Maureen_Orth
http://en.wikipedia.org/wiki/Maurice_R._Greenberg
http://en.wikipedia.org/wiki/Maxine_Waters
http://en.wikipedia.org/wiki/Maynard_Jackson
http://en.wikipedia.org/wiki/Meg_Tilly
http://en.wikipedia.org/wiki/Megawati_Sukarnoputri
http://en.wikipedia.org/wiki/Mel_Karmazin
http://en.wikipedia.org/wiki/Mia_Hamm
http://en.wikipedia.org/wiki/Michael
http://en.wikipedia.org/wiki/Michael_Bloomberg
http://en.wikipedia.org/wiki/Michael_Crichton
http://en.wikipedia.org/wiki/Michael_Jackson
http://en.wikipedia.org/wiki/Michael_M._Sears
http://en.wikipedia.org/wiki/Michael_Milken
http://en.wikipedia.org/wiki/Michael_Moore
http://en.wikipedia.org/wiki/Michael_Newdow
http://en.wikipedia.org/wiki/Michael_Weisskopf
http://en.wikipedia.org/wiki/Michael_Welner
http://en.wikipedia.org/wiki/Michel_(name)
http://en.wikipedia.org/wiki/Micheline_Calmy-Rey
http://en.wikipedia.org/wiki/Michelle_Malkin
http://en.wikipedia.org/wiki/Mickey_Kaus
http://en.wikipedia.org/wiki/Mike_Boettcher
http://en.wikipedia.org/wiki/Mike_Espy
http://en.wikipedia.org/wiki/Mike_Galanos
http://en.wikipedia.org/wiki/Mike_Hanna
http://en.wikipedia.org/wiki/Mikhail_Gorbachev
http://en.wikipedia.org/wiki/Mirjana_Marković
http://en.wikipedia.org/wiki/Mohamed_ElBaradei
http://en.wikipedia.org/wiki/Mohammad_Khatami
http://en.wikipedia.org/wiki/Mohammed_A._Aldouri
http://en.wikipedia.org/wiki/Muhammad_(name)
http://en.wikipedia.org/wiki/Muhammad_Zaidan
http://en.wikipedia.org/wiki/Nam_Cam
http://en.wikipedia.org/wiki/Nancy_(given_name)
http://en.wikipedia.org/wiki/Nancy_Grace
http://en.wikipedia.org/wiki/Nat_Hentoff
http://en.wikipedia.org/wiki/Natalie_Maines
http://en.wikipedia.org/wiki/Nelson_Mandela
http://en.wikipedia.org/wiki/Nic_Robertson
http://en.wikipedia.org/wiki/Nicholas
http://en.wikipedia.org/wiki/Norman_Mineta
http://en.wikipedia.org/wiki/Norman_Schwarzkopf,_Jr.
http://en.wikipedia.org/wiki/O._J._Simpson
http://en.wikipedia.org/wiki/Ozzy_Osbourne
http://en.wikipedia.org/wiki/Patty_Murray
http://en.wikipedia.org/wiki/Paul_(name)
http://en.wikipedia.org/wiki/Paul_Begala
http://en.wikipedia.org/wiki/Paul_McCartney
http://en.wikipedia.org/wiki/Paul_Silas
http://en.wikipedia.org/wiki/Paul_Wolfowitz
http://en.wikipedia.org/wiki/Paula_Zahn
http://en.wikipedia.org/wiki/Peggy_(given_name)
http://en.wikipedia.org/wiki/Peggy_Noonan
http://en.wikipedia.org/wiki/Pervez_Musharraf
http://en.wikipedia.org/wiki/Pete_Gillen
http://en.wikipedia.org/wiki/Pete_Rose
http://en.wikipedia.org/wiki/Peter_(name)
http://en.wikipedia.org/wiki/Peter_Arnett
http://en.wikipedia.org/wiki/Peter_Bergen
http://en.wikipedia.org/wiki/Peter_Cosgrove
http://en.wikipedia.org/wiki/Peter_Pace
http://en.wikipedia.org/wiki/Peter_T._King
http://en.wikipedia.org/wiki/Phil_Donahue
http://en.wikipedia.org/wiki/Phil_Jackson
http://en.wikipedia.org/wiki/Plácido_Domingo
http://en.wikipedia.org/wiki/President_of_the_United_States
http://en.wikipedia.org/wiki/Rafic_Hariri
http://en.wikipedia.org/wiki/Ralph_Nader
http://en.wikipedia.org/wiki/Raúl_Reyes
http://en.wikipedia.org/wiki/Rebecca_Lee
http://en.wikipedia.org/wiki/Recep_Tayyip_Erdoğan
http://en.wikipedia.org/wiki/Reggie_White
http://en.wikipedia.org/wiki/Regina_Peruggi
http://en.wikipedia.org/wiki/Renee
http://en.wikipedia.org/wiki/Richard
http://en.wikipedia.org/wiki/Richard_Lugar
http://en.wikipedia.org/wiki/Richard_Myers
http://en.wikipedia.org/wiki/Richard_Nixon
http://en.wikipedia.org/wiki/Richard_Parsons_(businessman)
http://en.wikipedia.org/wiki/Richard_Quest
http://en.wikipedia.org/wiki/Robert
http://en.wikipedia.org/wiki/Robert_Blake_(actor)
http://en.wikipedia.org/wiki/Robert_Byrd
http://en.wikipedia.org/wiki/Robert_Chambers_(killer)
http://en.wikipedia.org/wiki/Robert_Dallek
http://en.wikipedia.org/wiki/Robert_L._Johnson
http://en.wikipedia.org/wiki/Robert_Mueller
http://en.wikipedia.org/wiki/Robert_Novak
http://en.wikipedia.org/wiki/Robin_(name)
http://en.wikipedia.org/wiki/Rod_Stewart
http://en.wikipedia.org/wiki/Roger
http://en.wikipedia.org/wiki/Roger_Clemens
http://en.wikipedia.org/wiki/Roh_Moo-hyun
http://en.wikipedia.org/wiki/Roméo_Dallaire
http://en.wikipedia.org/wiki/Ronald_Reagan
http://en.wikipedia.org/wiki/Rudi_Bakhtiar
http://en.wikipedia.org/wiki/Rudy_Giuliani
http://en.wikipedia.org/wiki/Rush_Limbaugh
http://en.wikipedia.org/wiki/Ryan_(given_name)
http://en.wikipedia.org/wiki/Salman_Rushdie
http://en.wikipedia.org/wiki/Sam_Nunn
http://en.wikipedia.org/wiki/Sam_Sloan
http://en.wikipedia.org/wiki/Samir_(name)
http://en.wikipedia.org/wiki/Samuel_D._Waksal
http://en.wikipedia.org/wiki/Sanjay_Gupta
http://en.wikipedia.org/wiki/Sarah_(given_name)
http://en.wikipedia.org/wiki/Sean_Hannity
http://en.wikipedia.org/wiki/Sergey_Yastrzhembsky
http://en.wikipedia.org/wiki/Seán_Patrick_O'Malley
http://en.wikipedia.org/wiki/Shaquille_O'Neal
http://en.wikipedia.org/wiki/Sharon
http://en.wikipedia.org/wiki/Shirley_Temple
http://en.wikipedia.org/wiki/Stanley_A._McChrystal
http://en.wikipedia.org/wiki/Stephen
http://en.wikipedia.org/wiki/Stephen_A._Douglas
http://en.wikipedia.org/wiki/Steve_Jobs
http://en.wikipedia.org/wiki/Steve_Wynn_(entrepreneur)
http://en.wikipedia.org/wiki/Strom_Thurmond
http://en.wikipedia.org/wiki/Susan_(given_name)
http://en.wikipedia.org/wiki/Susan_Candiotti
http://en.wikipedia.org/wiki/Sylvester_Stallone
http://en.wikipedia.org/wiki/Taylor_(given_name)
http://en.wikipedia.org/wiki/Ted_Kennedy
http://en.wikipedia.org/wiki/Terry_Nichols
http://en.wikipedia.org/wiki/Theo_van_Gogh_(film_director)
http://en.wikipedia.org/wiki/Theodore_Kaczynski
http://en.wikipedia.org/wiki/Thomas_(name)
http://en.wikipedia.org/wiki/Thomas_Andrews_(politician)
http://en.wikipedia.org/wiki/Thurgood_Marshall
http://en.wikipedia.org/wiki/Tim_Kaine
http://en.wikipedia.org/wiki/Timothy_J._Roemer
http://en.wikipedia.org/wiki/Timothy_McVeigh
http://en.wikipedia.org/wiki/Tipper_Gore
http://en.wikipedia.org/wiki/Tom_Brokaw
http://en.wikipedia.org/wiki/Tom_Daschle
http://en.wikipedia.org/wiki/Tom_DeLay
http://en.wikipedia.org/wiki/Tom_Ridge
http://en.wikipedia.org/wiki/Tommy_Franks
http://en.wikipedia.org/wiki/Tommy_Tuberville
http://en.wikipedia.org/wiki/Tony_Blair
http://en.wikipedia.org/wiki/Toujan_al-Faisal
http://en.wikipedia.org/wiki/Tucker_Carlson
http://en.wikipedia.org/wiki/Vanna
http://en.wikipedia.org/wiki/Vincent
http://en.wikipedia.org/wiki/W._Patrick_Lang
http://en.wikipedia.org/wiki/William_(name)
http://en.wikipedia.org/wiki/William_Cohen
http://en.wikipedia.org/wiki/William_Perry
http://en.wikipedia.org/wiki/Willie_Nelson
http://en.wikipedia.org/wiki/Wolf_Blitzer
http://en.wikipedia.org/wiki/Yasmin
http://en.wikipedia.org/wiki/Yasser_Abd_Rabbo
http://en.wikipedia.org/wiki/Yasser_Arafat
'''.strip().split())
assert all([pool[i - 1] < pool[i]
            for i in range(1, 425)]), 'pool is not sorted'

out_f = io.open(args.out_fn, 'w', encoding='utf-8')
for fn in xrange(1, 110):
    with open(args.thrift_data_dir + '/%03d' % fn) as f:
        p = TBinaryProtocol.TBinaryProtocolAccelerated(
            TFileObjectTransport(f))
        while True:
            try:
                pp.read(p)
            except EOFError:
                break
            for m in pp.mentions:
                c = m.context
                if c is not None:
                    url = m.wiki_url
                    if url in pool:
                        # out_f.write
                        print url, '|||', c.left, c.middle, c.right
