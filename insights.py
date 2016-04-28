#!/usr/bin/env python

import argparse
import ujson as json
import sys
import datetime

from src import analysis,output,search

##
## analysis functions
##

def run_full_tweet_input(input_generator, conversation_results, audience_results): 
    """ iterate over Tweets and analyze"""
    user_ids = set()
    for line in input_generator: 
        try:
            tweet = json.loads(line)  
            # account for compliance and other non-standard tweet payloads
            if "actor" not in tweet:
                continue
            if conversation_results is not None:
                analysis.analyze_tweet(tweet,conversation_results)
            if audience_results is not None:
                user_id = int(tweet["actor"]["id"].split(":")[2])
                if user_id not in user_ids:
                    bio = tweet["actor"]["summary"] 
                    if bio is not None and bio != "":
                        analysis.analyze_bio(tweet,audience_results)
                    user_ids.add( user_id ) 
        except ValueError:
            continue
        
    if audience_results is not None:
        analysis.analyze_user_ids(user_ids,audience_results)


def run_tweet_id_input(input_generator,conversation_results,audience_results):
    """ iterate over Tweet IDs and analyze"""
    tweet_ids = set([tweet_id for tweet_id in input_generator])

    user_ids = []
    # this might not scale 
    try:
        tweets = search.get_tweets_from_ids(tweet_ids)
    except NotImplementedError: 
        tweets = []
    for tweet in tweets: 
        if conversation_results is not None:
            analysis.analyze_tweet(tweet,conversation_results)
        
        if audience_results is not None:
            user_id = int(tweet["actor"]["id"].split(":")[2]) 
            if user_id not in user_ids:
                #bio = tweet["actor"]["summary"]
                analysis.analyze_bio(tweet,audience_results)
                user_ids.append( user_id) 
    
    if audience_results is not None:         
        analysis.analyze_user_ids(user_ids,audience_results)

def run_user_id_input(input_generator,conversation_results,audience_results):
    """ iterate over user IDs and analyze"""
    user_ids = [user_id for user_id in generator]
    user_ids = set(user_ids)

    if audience_results is not None:
        analysis.analyze_user_ids(user_ids,audience_results)

    # this might not scale
    try:
        tweets = search.get_tweets_from_user_ids(user_ids) 
    except NotImplementedError:
        tweets = []
    for tweet in tweets: 
        if conversation_results is not None: 
            analysis.analyze_tweet(tweet,conversation_results)
    
        if audience_results is not None:
            user_id = int(tweet["actor"]["id"].split(":")[2]) 
            bio = tweet["actor"]["summary"]
            analysis.analyze_bio(bio,user_id,audience_results) 

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--identifier",dest="unique_identifier", default=None,
            help="a unique name to identify the conversation/audience")
    parser.add_argument("-c","--do-conversation-analysis",dest="do_conversation_analysis",action="store_true",default=False,
            help="do conversation analysis on Tweets")
    parser.add_argument("-a","--do-audience-analysis",dest="do_audience_analysis",action="store_true",default=False,
            help="do audience analysis on users") 
    parser.add_argument("-i","--input-file-name",dest="input_file_name",default=None,
            help="file containing tweets, tweet IDs, or user IDs; take input from stdin if not present")
    parser.add_argument("-f","--full-tweet-input",dest="full_tweet_input",action="store_true",default=False,
            help="input is JSON-formatted tweet data")
    parser.add_argument("-t","--tweet-id-input",dest="tweet_id_input",action="store_true",default=False,
            help="input is tweet IDs") 
    parser.add_argument("-u","--user-id-input",dest="user_id_input",action="store_true",default=False,
            help="input is user IDs") 
    args = parser.parse_args()

    # sanity checking
    if (args.full_tweet_input and args.tweet_id_input) or (args.full_tweet_input and args.user_id_input) or (args.tweet_id_input and args.user_id_input):
        sys.stderr.write("Must not choose more than one input type.\n")
        sys.exit()

    if (args.full_tweet_input is False and args.tweet_id_input is False and args.user_id_input is False):
        sys.stderr.write("Must choose one input type.\n")
        sys.exit()
    
    # get the time right now, to use in output naming
    time_string = datetime.datetime.now().isoformat().split(".")[0].translate(None,":")

    # creat dictionaries for results requested
    # entries in these dictionaries map measurement names to data collections
    # start by creating a unique ID from the audience/conversation identifier and the current time
    if args.do_audience_analysis:
        audience_results = {"unique_id": args.unique_identifier + "_" + time_string} 
    else:
        audience_results = None
    if args.do_conversation_analysis:
        conversation_results = {"unique_id": args.unique_identifier + "_" + time_string} 
    else:
        conversation_results = None

    # manage input source
    if args.input_file_name is not None:
        input_generator = open(args.input_file_name)
    else:
        input_generator = sys.stdin

    # manage input format
    if args.full_tweet_input:
        run_full_tweet_input(input_generator,conversation_results,audience_results)
    if args.tweet_id_input:
        run_tweet_id_input(input_generator,conversation_results,audience_results)
    if args.user_id_input:
        run_user_id_input(input_generator,conversation_results,audience_results)

    # format and dump results
    if args.do_conversation_analysis:
        analysis.summarize_tweets(conversation_results,args)
        output.dump_conversation(conversation_results,args)
    if args.do_audience_analysis:
        analysis.summarize_audience(audience_results,args)
        output.dump_audience(audience_results,args)
