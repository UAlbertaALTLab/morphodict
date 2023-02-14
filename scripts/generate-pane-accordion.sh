#!/bin/sh

# Usage:
#    cat 0:LAYOUT.tsv | ./generate-pane-accordion.sh 1:RELABEL.tsv 2:RELABEL-COLUMN{0|1|2|...} 3:OUTPUT{=txt|html} 4:FST.{hfst,hfstol} 5:LEMMA

# Example(s):
#    cat ~/altdev/morphodict/src/CreeDictionary/res/layouts/VAI/revised/VTA.tsv | ./generate-pane-accordion.sh  ~/altdev/morphodict/src/CreeDictionary/res/crk.altlabel.tsv 4 'html' | less
#    cat ~/altdev/morphodict/src/CreeDictionary/res/layouts/VAI/revised/VTA.tsv | ./generate-pane-accordion.sh  ~/altdev/morphodict/src/CreeDictionary/res/crk.altlabel.tsv 0 'txt' | less
# cat ~/altdev/morphodict/src/CreeDictionary/res/layouts/VAI/revised/VAI.tsv | ./generate-pane-accordion.sh  ~/altdev/morphodict/src/CreeDictionary/res/crk.altlabel.tsv 4 'html' ~/giellalt/lang-crk/src/crk-strict-generator-with-morpheme-boundaries-giellaltbuild.hfstol nipâw > VAI.html

gawk '{ if(NF==0) gsub("^\t+",""); print; }' |

gawk -v RELABEL=$1 -v STYLE=$2 -v OUTPUT=$3 -v FST=$4 -v LEMMA=$5 'BEGIN { FS="\t";
output=tolower(OUTPUT); relabel_file=RELABEL; style=STYLE; fst_gen=FST; lemma=LEMMA;

  if(output!="html" && output!="txt")
    output="txt";
  while((getline rl < relabel_file)!=0)
    {
      nf=split(rl, f, "\t");
      if(nf>=2)
        ++nr;
      if(nr>=2 && nf>=2 && index(f[1],"^PV/")==0)
        if(nf>=2)
          for(i=2; i<=nf; i++)
             {
               gsub("\\+", "@", f[1]);
               if(length(f[1])>=1)
                 {
                   gsub(" ", "#", f[i]);
                   rlab[f[1], i]="#" f[i] "#";
                   rlen[f[1]]=length(f[1]);
                 }
             }
    }

  RS=""; FS="\n";
}
{
  sub("[ \t]+$", "", $1);
  gsub("[ ]*\t+[ ]*", "\t", $1);
  nh=split($1, h, "\t");
  for(c=1; c<=nh; c++)
     head[++cc]=h[c];

  for(r=2; r<=NF; r++)
     {
       sub("[ \t]+$", "", $r);
       gsub("[ ]*\t+[ ]*","\t",$r);
       nc=split($r, f, "\t");
       for(c=2; c<=nc; c++)
          {
            # ff[r, c]=f[c];
            cell[h[c]][r]=f[c];
            row[h[c]][r]=f[1];
          }
     }

}

# <button class="accordion">Section 1</button>
# <div class="panel">
#   <table colspan="2">
#   <tr><td>A</td><td>B</td></tr>
#   <tr><td>C</td><td>D</td></tr>
#   </table>
# </div>

END {
 if(output=="html")
   {
     printf "<!DOCTYPE html>\n";
     printf "<html>\n";
     printf "<head>\n";
     printf "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">";
     printf "<style>\n";
     printf ".accordion {\n";
     printf "   background-color: #eee;\n";
     printf "   color: #444;\n";
     printf "   cursor: pointer;\n";
     printf "   padding: 18px;\n";
     printf "   width: 100%;\n";
     printf "   border: none;\n";
     printf "   text-align: left;\n";
     printf "   outline: none;\n";
     printf "   font-size: 15px;\n";
     printf "   transition: 0.4s;\n";
     printf " }\n";

     printf ".active, .accordion:hover {\n";
     printf "    background-color: #ccc;\n";
     printf " }\n";

     printf ".panel {\n";
     printf "   padding: 0 18px;\n";
     printf "   display: none;\n";
     printf "   background-color: white;\n";
     printf "   overflow: hidden;\n";
     printf "}\n";
     printf "</style>\n";
     printf "</head>\n";
     printf "<body>\n";
     printf "\n";
  }

 PROCINFO["sorted_in"]="@ind_num_asc";
 for(hh in head)
  if(head[hh]!="")
  {
    if(output=="txt")
      printf "%s\n", relabel(head[hh], style);
    else
      {
        printf "<button class=\"accordion\">%s</button>\n", relabel(head[hh], style);
        printf "<div class=\"panel\">\n";
        printf "<table colspan=\"2\">\n";
      }
    for(r in cell[head[hh]])
       if(output=="txt")
         printf "%s\t%s\n", relabel(row[head[hh]][r], style), relabel(cell[head[hh]][r], style);
       else
         if(lemma=="")
           printf "<tr><th>%s</th><th>%s</th></tr>\n", relabel(row[head[hh]][r], style), relabel(cell[head[hh]][r], style);
         else
           {
             anl=cell[head[hh]][r];
             printf "<tr><td>%s</td>", relabel(row[head[hh]][r], style);
             if(match(anl, "\\$\\{lemma\\}")!=0)
               {
                 sub("\\$\\{lemma\\}", lemma, anl);
                 if(match(fst_gen, "\\.hfst$")!=0)
                   hfst="hfst-lookup";
                 if(match(fst_gen, "\\.hfstol$")!=0)
                   hfst="hfst-optimized-lookup";
                 form=lookup(hfst " -q", fst_gen, anl);
                 if(form==anl || form=="+?")
                   form="&mdash;";
                 else
                   {
                     gsub("[<>/]", "\\&middot;", form);
                     gsub("\n", "<br>", form);
                   }
                 printf "<td>%s</td></tr>\n", form;
               }
             else
               printf "<td>%s</td></tr>\n", relabel(cell[head[hh]][r], style);
           }
    if(output=="txt")
      printf "\n";
    else
      {
        printf "</table>\n";
        printf "</div>\n";
        printf "\n";
      }
  }

  if(output=="html")
    {

# <script>
# var acc = document.getElementsByClassName("accordion");
# var i;
# 
# for (i = 0; i < acc.length; i++) {
#   acc[i].addEventListener("click", function() {
#     this.classList.toggle("active");
#     var panel = this.nextElementSibling;
#     if (panel.style.display === "block") {
#       panel.style.display = "none";
#     } else {
#       panel.style.display = "block";
#     }
#   });
# }
# </script>

      printf "\n";
      printf "<script>\n";
      printf "var acc = document.getElementsByClassName(\"accordion\");\n";
      printf "var i;\n";
      printf "\n";
      printf "for (i = 0; i < acc.length; i++) {\n";
      printf "acc[i].addEventListener(\"click\", function() {\n";
      printf "  this.classList.toggle(\"active\");\n";
      printf "  var panel = this.nextElementSibling;\n";
      printf "  if (panel.style.display === \"block\") {\n";
      printf "    panel.style.display = \"none\";\n";
      printf "  } else {\n";
      printf "    panel.style.display = \"block\";\n";
      printf "  }\n";
      printf "});\n";
      printf "}\n";
      printf "\n";
      printf "</script>\n";
      printf "\n";
      printf "</body>\n";
      printf "</html>\n";
    }
}

function relabel(str, st,     format)
{
  if(match(str, "^[_\\|\\*]")!=0 && st!=0)
    {
      format="";
      if(match(str, "^\\*")!=0)
        format="heading";
      if(match(str, "^_")!=0)
        format="rowlabel";
      if(match(str, "^\\|")!=0)
        format="collabel";
      if(format=="")
        format="cell";

      sub("^[\\*\\|_ ]*", "", str);
      gsub("[ ]*[\\*\\|_\\+][ ]*", "@", str);
      pinfo=PROCINFO["sorted_in"];
      PROCINFO["sorted_in"]="@val_num_desc";
      for(l in rlen)
         if(match(str, "(^|_|@)" l "(_|@|$)")!=0 && rlen[l]>=1)
            {
              sub(l, rlab[l, st], str);
            }
      sub("^#+", "", str);
      sub("#+$", "", str);
      gsub("#+", " ", str);
      gsub("@", " – ", str);
      gsub("[ ]+", " ", str);

      # Formatting row/column label
      if(format=="heading")
        str="<b>" str "</b>";
      if(format=="rowlabel")
        str="<em><b>" str "</b></em>";
      if(format=="collabel")
        str="<em><b>" str "</b></em>";

      PROCINFO["sorted_in"]=pinfo;
      return(str);
    }
  else
    return(str);
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
