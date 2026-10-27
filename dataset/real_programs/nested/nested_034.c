// category: nested  (real program 034)
// Codeforces submission 447656, problem 84/A, GNU C++, 2011-05-13
// https://codeforces.com/contest/84/submission/447656
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <vector>
#include <list>
#include <map>
#include <set>
#include <queue>
#include <deque>
#include <stack>
#include <bitset>
#include <algorithm>
#include <functional>
#include <numeric>
#include <utility>
#include <sstream>
#include <iostream>
#include <iomanip>
#include <cstdio>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <cstring>

using namespace std;

#define FOR(i,a,b) for (int i(a); i < (b); i++) 
#define REP(i,n) FOR(i,0,n) 

int main(){
	int n;
	scanf("%d",&n);
	printf("%d\n",2*n-(n+1)/2);
	return 0;
}
