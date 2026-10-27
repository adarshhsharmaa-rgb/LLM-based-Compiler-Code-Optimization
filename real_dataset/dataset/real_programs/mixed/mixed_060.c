// category: mixed  (real program 060)
// Codeforces submission 36444831, problem 950/A, GNU C++, 2018-03-21
// https://codeforces.com/contest/950/submission/36444831
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>
int main(){
 int r,l,a,cont=0,sobras=0;
 scanf("%d%d%d",&r,&l,&a);
 if(r>=l){
  cont+=l;
  sobras=r-l;
  
 }
 else if(l>r){
  cont+=r;
  sobras=l-r; 
 }
 //printf("%d\n",cont);
  //printf("%d %d +%d\n",sobras,a,cont);
 while(sobras>0 && a>0){
  sobras--;
  a--;
  cont++;
  //printf("%d %d +%d\n",sobras,a,cont);
 }
 cont+=a/2;
 printf("%d\n",cont*2);
 
 return 0;
}
