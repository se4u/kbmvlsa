import pickle
import argparse
arg_parser = argparse.ArgumentParser(
    description='Denormalize ACE, ACEtoWiki data')
arg_parser.add_argument('--wikilink_category_pkl_fn',
                        default="data/wikilink_category.pkl", type=str)
args = arg_parser.parse_args()

wikilink_category = pickle.load(open(args.wikilink_category_pkl_fn, "rb"))
category_to_link = wikilink_category['category_to_link']
abundant_categories = [
    k for k, e in category_to_link.items() if len(set(e)) > 10]
print(len(abundant_categories))
# 194
print abundant_categories

# ['United States Army soldiers', 'Presidential Medal of Freedom recipients',
#  'American Methodists', 'American people of English descent', 'Baptists from the United States',
#  'Democratic Party members of the United States House of Representatives', '21st-century American politicians',
#  'United States Army generals', 'American philanthropists',
#  'Presidents of the United States', 'American people of Irish descent',
#  'American people of German descent', 'Honorary Knights Commander of the Order of the British Empire',
#  'Recipients of the Order of the Cross of Terra Mariana, 1st Class', 'Virginia Democrats',
#  'Democratic Party (United States) presidential nominees', 'Fellows of the American Academy of Arts and Sciences',
#  'Grammy Award winners', '21st-century American male actors',
#  'Recipients of the Bronze Star Medal', 'Democratic Party United States Senators',
#  'Participants in American reality television series', 'Republican Party members of the United States House of Representatives',
#  'American gun control advocates', 'CNN people',
#  'American Roman Catholics', 'American television news anchors',
#  'American anti-communists', 'American political writers',
#  'Heads of state', 'Harvard University alumni',
#  'Clinton Administration cabinet members', 'American autobiographers',
#  'American women journalists', '20th-century American businesspeople',
#  'Texas Republicans', 'American political pundits',
#  'American military personnel of the Vietnam War', 'Harvard Law School alumni',
#  'American male journalists', 'American television personalities',
#  'New York Republicans', 'Recipients of the Air Medal',
#  '21st-century American businesspeople', '21st-century American writers',
#  'American football quarterbacks', 'American memoirists',
#  'United States presidential candidates, 2004', '20th-century American writers',
#  'American male film actors', 'American male writers',
#  '20th-century American politicians', 'Peabody Award winners',
#  'All-American college football players', 'Recipients of the Legion of Merit',
#  'Republican Party state governors of the United States', 'American people of Italian descent',
#  'New York Democrats', 'American television reporters and correspondents',
#  'Democratic Party state governors of the United States', 'American people of Scottish descent',
#  'American Jews', 'American military personnel of World War II',
#  'Recipients of the Purple Heart medal', 'American billionaires',
#  'Yale University alumni', 'American broadcast news analysts']


print (category_to_link['Clinton Administration cabinet members'])
# ['Janet_Reno', 'Lloyd_Bentsen', 'Norman_Mineta', 'Al_Gore', 'William_Cohen',
# 'Bruce_Babbitt', 'Federico_Pe%C3%B1a', 'Henry_Cisneros', 'Dan_Glickman',
# 'Ron_Brown_(U.S._politician)', 'Lawrence_Summers', 'Bill_Richardson',
# 'Richard_Riley', 'William_Perry', 'Mike_Espy', 'Les_Aspin']
