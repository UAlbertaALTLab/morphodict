#/bin/sh

# Usage:
#   cat ~/altlab2/crk/dicts/crkeng_dictionary.importjson | scripts/top-coca-vs-dict-eng-def-matches.sh 100 ~/altlab/eng/generated/COCA_wordFrequency.txt 'n|v|j|r' 'definition' full | less

gawk -v TOP=$1 -v COCA=$2 -v POS=$3 -v SENSE=$4 -v REPORT=$5 'BEGIN { top=TOP; coca_freq_file=COCA; report=REPORT; npos=split(POS,pos_ix,"[\\|/]");
  if(npos==0)
    {
      pos_ix[1]="n"; pos_ix[2]="v"; pos_ix[3]="j"; pos_ix[4]="r"; npos=4;
    }
  for(i=1; i<=npos; i++)
       pos[pos_ix[i]]=pos_ix[i];
  if(SENSE!="")
    sense_field=SENSE;
  else
    sense_field="definition";
  while((getline < coca_freq_file)!=0)
       { gsub("\r",""); # Removing Windows CR character
         if($3 in pos && length($2)>=3)
           { if($2!=lemma)
               { lemma=$2; lemmas[++n]=lemma; }
             if(n<=top && !(tolower($6) in form2lemma))
               {
                 form2lemma[tolower($6)]=lemma;
                 # lemmas[n]=lemma;
                 if(length(lemma)>llemma)
                   llemma=length(lemma);
               }
           }
       }
#   if(report=="full")
#     printf "ENTRIES WITH NO WORD IN TOP %i\n", top;
}
{
  m=match($0,"\""sense_field"\": \"([^\"]+)\"",f);
  if(m!=0)
    {
      nentries++;
      nw=split(f[1],w,"[ /,;:\\(\\)\\[\\]\"]+");
      hits=0;
      for(i=1; i<=nw; i++)
         if(tolower(w[i]) in form2lemma)
           {
             hits++;
             lemmahits[form2lemma[tolower(w[i])]]++;
           }
      if(hits!=0)
        entryhits++;
#       if(hits==0 && report=="full")
#         printf "%s\n", f[1];
    }
}
END { if(report=="full") printf "MATCHES OF TOP %i COCA LEMMAS IN ENTRIES:\n", top;
  for(i=1; i<=top; i++)
         {
           if(lemmas[i] in lemmahits)
             nlemmahits++;
           if(report=="full")
             printf "i=%-"length(top)"i n=%-6i %"llemma"s\n", i, lemmahits[lemmas[i]], lemmas[i];
         }
      if(report!="full")
        {
          printf "ENTRY MATCHES IN TOP %i LEMMAS: %i/%i\n", top, entryhits, nentries;
          printf "ENTRY WORD MATCHES IN TOP %i LEMMAS: %i/%i\n", top, nlemmahits, top;
        }
}'

