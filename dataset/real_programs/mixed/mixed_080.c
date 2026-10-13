// category: mixed  (real program 080)
// Codeforces submission 36702747, problem 922/C, C++14 (GCC 6-32), 2018-03-28
// https://codeforces.com/contest/922/submission/36702747
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include "bits/stdc++.h"
 using namespace std;

 int main(){
  long long N , k , i;
  scanf( "%lld%lld" , &N , &k );

  if( k > 100 ){
   puts( "NO" );
   return 0;
  }

  for( i = 1 ; i <= k ; ++i ){
   if( N % i != i - 1 ){
    puts( "NO" );
    return 0;
   }
  }

  puts( "Yes" );
  return 0;
 }
