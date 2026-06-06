SEC ADV Data Mapping

Question Number in Form Adv
Column Letter
Column Header in Report
Why
1E1
B
Organization CRD#
It's the unique ID that maps directly to their SEC profile URL — adviserinfo.sec.gov/firm/summary/{CRD#}. 

That gives you a one-click link to their full filing, key personnel, disclosures, and history. Useful for research before outreach.
1B1
K
Primary Business Name
Name of firm
1F1
M
Main Office Street Address 1
Address
1F1
O
Main Office City
City
1F1
P
Main Office State
State
1F3
T
Phone Number
Contact Number
1F5
V
Total number of offices, other than your Principal Office and place of business
Gives an idea on the size of the firm and subsidiaries. Large numbers likely won’t be a great fit. 

Want to have a size that would be open to working with a smaller firm like PGP


AG
Latest ADV Filing Date
Gives an idea of the accuracy of the information. 

Older dates suggest these numbers may be outdated, giving less confidence in the conclusions of assessment.
1I
AK
Total Number of Website Addresses
Strong indicator of digital presence and social media activity
1I
AJ
Website URL
Main website they share with SEC
1O
AV
$1B or more in assets on last day of most recent fiscal year?
Y or N. PGP likely targeting those with the answer “N” 
1O - if yes
AW
If yes, what is the approximate amount of your assets:
Ranges of $1-10B, $10-50B, and $50B+. 

Gives sense of size. As of 3/26, PGP is likely targeting $1-10B AT MOST. 

More likely than not, the $300M-1B range 
3B
BM
In what month does your fiscal year end each year?
If the end is near, higher likelihood of assessing budgets and potentially shopping for new partners.
5A
BV
How many full-time and part-time employees?
PGP is likely looking to work with firms with leaner teams. 30 or less.

Less bureaucracy and streamlined decision making workflow.
5B1
BW
How many employees perform advisor functions (including research)?
Indicates number of advisors. 

Again, looking for leaner teams, likely less than 20
5Da1
DH
Number of individual clients (excluding HNWI)
Concentration of client base that are not HNWI
5Da3
DJ
AUM of individuals
AUM of non-HNWI client base
5Db1
DK
Number of HNWI clients
Concentration of client base that are HNWI
5Db3
DM
AUM of HNWI
AUM of HNWI client base.

High concentration could indicate AUM at-risk due to HNW and likely older clients
5E1
EV
Compensation via % of AUM
My ICP uses % as model. Revenue is directly tied to AUM. 

Must be “Y”
5E5
EZ
Commissions for services
Not a true independent RIA and don’t want to work with these conflict of interest firms. 

Must be “N” (May revisit depending on final list)
5F1
FD
Provide continuous management services?
Must be “Y”
5F2a
FE
Discretionary $ amount
Total AUM where advisor has full control of decisions
5F2d
FH
Number of discretionary accounts
We want to target firms with more of this than non-discretionary. 

Discretionary implies a stickier relationship with clients.
5F2b
FF
Non-discretionary $ amount
Advisor suggests/recommends but client must approve every decision
5F2e
FI
Number of non-discretionary accounts
Too much of this is not ideal for PGP likely. Less sticky relationship. 
5L1-4
KB-KI
Details on their marketing activity. 
If they answer N to all of them, they either don’t spend any $ on marketing at all, or tried and failed in the past. 

If they also have high HNWI concentration risk, PGP can be very useful to them.


Hard filters: 
Column EV=Y
You are compensated for your investment advisory services by: “a percentage of assets under your management”
Column EZ=N
You are compensated for your investment advisory services by: “Commissions”
Column FD=Y
Do you provide continuous and regular supervisory or management services to securities portfolios? “Yes”
Output columns:
Ensure outputs are all in lowercase and optimized for readability for scripts, code, AI, LLM, etc. Generally lowercase with underscores used in replace of spaces. 
CRD#, Business Name, Address, State, Website URL, Fiscal Year End Month, Team Size, Phone number, Advisor
Discretionary: # Accounts, AUM $, Avg per Account, % of Total AUM
Non-Discretionary: # Accounts, AUM $, Avg per Account, % of Total AUM
HNW Clients: # Accounts, AUM $, Avg per Account, % of Total AUM
Non-HNW Clients: # Accounts, AUM $, Avg per Account, % of Total AUM
Marketing Flag: "No Marketing" or "Has Marketing"
CRD#, Firm Name, Address, State, Website URL, Fiscal Year End Month, Team Size, Advisor Employees, Total AUM ($M), Disc AUM ($), Disc Accounts (#), Disc Avg per Account ($), Disc % of Total AUM, Non-Disc AUM ($)	, Non-Disc Accounts (#), Non-Disc Avg per Account ($), Non-Disc % of Total AUM, HNW Client Count (#), HNW AUM ($)	HNW Avg per Account ($)	HNW % of AUM	HNW % of Clients	Non-HNW Client Count (#)	Non-HNW AUM ($)	Non-HNW Avg per Account ($)	Non-HNW % of AUM	Non-HNW % of Clients	HNW Dependency Ratio	Total Clients (All Types)	Marketing Activity	Disciplinary Review	Latest ADV Filing Date	IAPD Profile
Data Analysis to Calculate
AUM Per Advisor: Total AUM/Adviser headcount (registered advisors, not always the number of employees total)
HNW Dependency Ratio = HNWI AUM / Total AUM 
Additional common scenarios to consider for firm activity
Jump in Total AUM
Changes in team size
Shift in AUM concentration and allocations
Shift in marketing presence
Change in number of offices
