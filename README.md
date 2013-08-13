twitter-sentiment-analysis-python
=================================

Tool to determine and visualize sentiment in tweets. Built using python + d3

=================================

This sentiment analysis tool takes any keyword and uses Twitter's Search API to retrieve the last 100 tweets containing the word. These tweets are then scored and the results visualized to give an overview of the real-time sentiment of the search term queried. 

At its core, the sentiment of each tweet is determined by scoring each word that makes up a tweet. The score is determined by matching every word against a [list of 2477 words](twittersentiment.s3.amazonaws.com/sentiment3.txt "Sentiment.txt") that have been given a predetermined score from +5 to -5. See the table below for a subset of this list:

Term	 Score <br>
abhor 	-3<br>
dislike	-2<br>
like  	+2<br>
admire	+3<br>

To obtain an even more accurate score, the following four strategies were utilized: 

1. Data cleansing
Once tweets were broken down into individual words they were stripped of any punctuation, converted to Unicode lowercase terms and compared against lists of Unicode lowercase terms. 

2. Negation
A negation term is one that precedes and negates the meaning of one of the pre-determined scored terms. For example, in the phrase “don’t like” don’t is the negation term. The full list of negation terms used in this tool can be found [here.](twittersentiment.s3.amazonaws.com/negation1.txt "Negation.txt") 

3. Intensifier
An intensifier is one that precedes and amplifies the meaning of one of the pre-determined scored terms. For example, in the phrase “really like” really is the intensifier. The full list of intensifiers used in this tool can be found [here.](twittersentiment.s3.amazonaws.com/intensitifer.txt "Intensitifer.txt")

The 4 scenarios below showcase how this tool calculates the effect of intensifiers and negation terms on a tweet: 

Keep in mind that the score for the term "like" is +2. 

negator term = -1 * [Score of term]. ex) don't like = -2 <br>
intensifier term = 2 * [Score of term]. ex) really like = +4 <br>
negator intensifier term = -0.5 * [Score of term]. ex) don't really like = -1 <br>
intensifier negator term = -2 * [Score of term]. ex) really don't like = -4 <br>

4. Slang and indicative terms
Looking through a random sample of 100,000 tweets from Twitter's Streaming API there were terms that statistically showed prominence for appearing in either positive or negative tweets. These terms along with their mean score were added to the list of scored terms. See the table below for a subset of this list:

Term	 Score<br>
luv	  +2<br>
hehe	+2<br>
:)  	+2<br>
:(  	-2<br>

Future Improvements
In its current version, this tool only analyzes English language tweets. Moreover, the scoring system can be improved in a number of ways ranging from scoring positive or negative phrases vs. individual words, having a multi-dimensional view of sentiment vs. a linear +/- score of sentiment, or having specific sentiment terms or phrases for specific brands or domains (ex: movies) which would be different than other domains.

Technology
This web app was built in python and utilizes the d3 JavaScript library as a way to visualize the results via a pie chart and word clouds. This is an open source project available on GitHub.

Thank you for your time and I hope your enjoy using this tool.
