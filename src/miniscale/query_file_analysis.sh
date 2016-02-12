QF=/export/projects/prastogi/kbvn/enron_contactgraph_queries
wc -l $QF
# Show the number of query words.
echo $(( (3151 - 493) ))
# Show the number of starting words.
cut -f 2- -d ' ' $QF | sed "s# #\n#g" | sort | uniq | wc -l
