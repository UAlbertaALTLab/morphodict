#/bin/sh

# Usage:
#   cat ~/altlab2/crk/dicts/crkeng_dictionary.importjson | scripts/top-coca-vs-dict-eng-def-matches.sh 100 ~/wordFrequency.txt full | less

gawk -v TOP=$1 -v COCA=$2 -v REPORT=$3 'BEGIN { top=TOP; report=REPORT; coca_freq_file=COCA;
  while((getline < coca_freq_file)!=0)
       { gsub("\r","");
         if(($3=="n" || $3=="v" || $3=="j" || $3=="r") && length($2)>=3)
           { if($2!=lemma)
               { lemma=tolower($2); lemmas[++n]=lemma; }
             if(n<=top && !($6 in form2lemma))
               {
                 form2lemma[$6]=lemma;
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
  m=match($0,"\"definition\": \"([^\"]+)\"",f);
  if(m!=0)
    {
      nentries++;
      nw=split(f[1],w,"[ /,;:\\(\\)\\[\\]\"]+");
      hits=0;
      for(i=1; i<=nw; i++)
         if(w[i] in form2lemma)
           {
             hits++;
             lemmahits[form2lemma[w[i]]]++;
           }
      if(hits!=0)
        entryhits++;
#       if(hits==0 && report=="full")
#         printf "%s\n", f[1];
    }
}
END { printf "MATCHES OF TOP %i COCA LEMMAS IN ENTRIES:\n", top;
  for(i=1; i<=top; i++)
         {
           if(lemmas[i] in lemmahits)
             nlemmahits++;
           if(report=="full")
             printf "i=%-"length(top)"i n=%-6i %"llemma"s\n", i, lemmahits[lemmas[i]], lemmas[i];
         }
      if(report=="full")
        printf "\n";
       printf "ENTRY MATCHES IN TOP %i LEMMAS: %i/%i\n", top, entryhits, nentries;
       printf "ENTRY WORD MATCHES IN TOP %i LEMMAS: %i/%i\n", top, nlemmahits, top;
}'

