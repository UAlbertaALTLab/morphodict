#!/bin/sh

gawk -v PARADIGM=$1 -v DICTIONARY=$2 -v CORPUS=$3 -v ENGGENFST=$4 'BEGIN { pdgm=PARADIGM; dict=DICTIONARY; corp=CORPUS; fst=ENGGENFST;

  # Read in entire corpus, extracting 1) lemma, 2) pos, and 3) lemma frequency
  fs=FS; rs=RS; FS="\t"; RS="\n";
  while((getline < corp)!=0)
     {
       anl0=$2; lemma=$4; freq=$3; pos=""; # print lemma, freq;
       if(match(anl0, "\\+(V)\\+(II|AI|TI|TA)", f)!=0)
         pos=f[1] f[2];
       if(match(anl0, "\\+(N)\\+(A|I)(\\+(D))?", f)!=0)
         pos=f[1] f[4] f[2];
       # if(!(lemma in frq))
       if(pos!="")
         frq[pos][lemma]=freq;
     }
  PROCINFO["sorted_in"]="@val_num_desc";
  # for(p in frq) for(l in frq[p]) print l, p, frq[p][l];
  for(p in frq)
     for(l in frq[p])
        {
          r=++ix[p];
          rank[p][r]=l;
        }
  FS=fs; RS=rs;
  # Test
  # PROCINFO["sorted_in"]="@ind_num_asc";
  # for(i in rank["VTA"])
  #    print i, rank["VTA"][i];
  # for(p in rank)
  #    for(i in rank[p])
  #       print i, rank[p][i];

  # Read in entire crk-to-eng dictionary, extracting 1) entry, 2) pos, and 3) senses
  fs=FS; rs=RS; FS="\n"; RS="";
  getline < dict;
  nr=split($0, rec, "\\},\n\\{");
  for(i=1; i<=nr; i++)
     {
       nf=split(rec[i], f, "\n");
       ns=0;
       for(j=1; j<=nf; j++)
          {
            if(match(f[j], "\"head\": \"([^\"]+)\"", ff)!=0) { entry=ff[1]; six=0; }
            if(match(f[j], "\"paradigm\": \"([^\"]+)\"", ff)!=0) pos=ff[1];
            if(match(f[j], "\"definition\": \"([^\"]+)\"", ff)!=0) sense[entry "_" pos][ff[1]]=++six;
	  }
     }
  # for(s in sense) for(d in sense[s]) print s, d;
  FS=fs; RS=rs;

  # Interpreting crk cell specifications and generating corresponding eng anl,
  # then outputting corresponding eng phrase
  while((getline < pdgm)!=0)
     {
       for(i=1; i<=NF; i++)
          if(match($i, "^(.*)\\$\\{lemma\\}(.*)$", f)!=0)
            {
              # Tag mapping from crk to eng
              crk_anl=f[1] "_" f[2];

              if(index(crk_anl, "+V+")!=0)
                {
                  if(index(crk_anl, "+V+II+")!=0) POS="VII";
                  if(index(crk_anl, "+V+AI+")!=0) POS="VAI";
                  if(index(crk_anl, "+V+TI+")!=0) POS="VTI";
                  if(index(crk_anl, "+V+TA+")!=0) POS="VTA";

                  tense=""; subj=""; obj=""; order="";
                  if(index(crk_anl, "+Cnj")!=0 && index(crk_anl, "PV/e+")!=0) order="Cnj+";
                  if(index(crk_anl, "PV/ki+")!=0) tense="Prt+";
                  if(index(crk_anl, "PV/ka+")!=0 && index(crk_anl, "+Cnj")==0) tense="Def+";
                  if(index(crk_anl, "PV/wi+")!=0) tense="Fut+";
                  if(index(crk_anl, "PV/ka+")!=0 && index(crk_anl, "+Cnj")!=0) tense="Inf+";
                  if(index(crk_anl, "+Cond")!=0) tense="Cond+";
                  if(index(crk_anl, "+Imp+Imm")!=0) tense="Imm+";
                  if(index(crk_anl, "+Imp+Del")!=0) tense="Del+";
                  if(match(crk_anl, "\\+([12345X][^\\+O]*)", f)!=0) subj=f[1] "+";
                  if(match(crk_anl, "\\+([12345X][^\\+O]*O)", f)!=0) obj=f[1] "+"
                  sub("12", "21", subj); sub("12", "21", obj);
                  sub("X","XPl", subj); sub("XO","XPlO", obj);
                  if(tense=="") tense="Prs+";
                  eng_anl=order tense subj obj; # print eng_anl;

                  # def="s/he sees s.o., s/he beholds s.o.; s/he recognizes s.o.; s/he witnesses s.o., s/he observes s.o., s/he bears witness to s.o.'\''s existence; s/he meets s.o., s/he encounters s.o."

                  # lemma=rank[POS][++pos_ix];
                  # lemma=rank["VTA"][3];
                  do { lemma=rank[POS][++pos_ix]; }
                  while (!(lemma "_" POS in sense));

                  PROCINFO["sorted_in"]="@val_num_asc";
                  # if(lemma "_" POS in sense)
                    for(def in sense[lemma "_" POS])
                     {
                       gsub("[ ]\\[[^\\]]+\\]", "", def);
                       gsub("[ ]\\(e\\.g\\.[^\\)]+\\)", "", def);
                       gsub("[ ]\\(i\\.e\\.[^\\)]+\\)", "", def);

                       six=sense[lemma "_" POS][def];

                       eng_phr=lookup("flookup -i -b", fst, eng_anl def);
                       printf "%i / %i - %s (%i): %s -> %s\t%s\n", pos_ix, six, lemma, frq["VTA"][lemma], crk_anl, eng_anl, eng_phr;
                     }
                }
            }
     }
}


function lookup(cmd, fst, input,     fst_output, inp, out, i, nr, nf, rs, fs)
{
  rs=RS; fs=FS;
  cmd_fst=cmd " " fst;

  # print input |& cmd_fst;
  # fflush(); close(cmd_fst, "to");
  # while((cmd_fst |& getline)!=0)
  #    {
  #      fst_output[++nr]=$0;
  #    }
  # fflush(); close(cmd_fst, "from");

  RS=""; FS="\n";
  print input |& cmd_fst;
  fflush(); close(cmd_fst, "to");
  cmd_fst |& getline inp;
  fflush(); close(cmd_fst, "from");
  RS=rs; FS=fs;

  nr=split(inp,fst_output,"\n");
  for(i=1; i<=nr; i++)
     {
       nf=split(fst_output[i],f,"\t");
       if(nf!=0)
         if(match(fst_output[i],"\\+\\?[\t$]")==0)
           out=out f[2] "\n";
         else
           out=out "+?" "\n";
     }
  sub("\n$","",out);
  
  return out;
}'

