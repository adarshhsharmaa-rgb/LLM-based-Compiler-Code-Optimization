// category: mixed  (real program 070)
// Codeforces submission 19299214, problem 268/B, MS C++, 2016-07-21
// https://codeforces.com/contest/268/submission/19299214
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>

#include <fstream>

#include <string>

#include <cstring>

#include <stdio.h>

#include <iomanip>

#include <cmath>

#include <vector>

#include<cctype>

#include<algorithm>

#include<set>

#include<stack>

#include<map>

#include<stdlib.h>

#include<ctime>

#include<iterator>

#include <deque>

#include <sstream>

#include<queue>

#include<cstdlib>

#include<climits>

#include<complex>





#define fn(i,n) for(int (i) = 0;(i) < (n);(i)++)

#define mk(f,s) make_pair((f),(s))



using namespace std;

typedef long long ll;



int main(){

	int n;

	scanf("%d",&n);

	int deg = 1;

	int ans = n;

	for(int i = n - 1;i > 1;i--){

		ans += i + (i - 1) * deg;

		deg++;

	}

	if(n != 1)

		ans++;

	printf("%d\n",ans);



	

	return 0;

}
