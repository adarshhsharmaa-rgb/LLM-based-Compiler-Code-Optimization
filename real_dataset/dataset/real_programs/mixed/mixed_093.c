// category: mixed  (real program 093)
// Codeforces submission 32866287, problem 897/B, C++14 (GCC 6-32), 2017-12-02
// https://codeforces.com/contest/897/submission/32866287
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;
typedef long long ll;

int main() {
  ll k, p;
  scanf("%lld %lld", &k, &p);
  ll sum = 0;

  ll r = 10;
  for (ll i = 1; i <= k; ++i) {
    if ((i / r) > 0) r *= 10;
    sum = (sum + (i * r) % p) % p;
  }

  for (ll i = 1; i <= k; ++i) {
    ll t = i;
    ll rev = 0;

    while (t != 0) {
      rev = rev * 10;
      rev = rev + t % 10;
      t = t / 10;
    }

    sum = (sum + rev) % p; 
  }

  printf("%lld\n", sum % p);
  return 0;
}
