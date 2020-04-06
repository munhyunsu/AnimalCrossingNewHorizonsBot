import os

import tweepy
import yaml

FLAGS = None
_ = None
CFG = None


def load_config():
    global FLAGS
    global CFG
    with open(FLAGS.config, 'r') as f:
        CFG = yaml.safe_load(f)
    return True


def main():
    if not load_config():
        print('Fail configuration file load')

    auth = tweepy.OAuthHandler(CFG['auth']['api_key'],
                               CFG['auth']['api_secret'])
    auth.set_access_token(CFG['auth']['access_token'],
                          CFG['auth']['access_token_secret'])
    api = tweepy.API(auth)

    cnt_retweeted = 0
    still_going = True
    for keyword in CFG['retweet']:
        for tweet in tweepy.Cursor(api.search, q=keyword, 
                                   result_type='recent').items(20):
            created_at = tweet.created_at
            url = (f'https://twitter.com/{tweet.user.screen_name}'
                   f'/status/{tweet.id}')
            print(f'{created_at} {url}')
            if tweet.retweeted:
                continue
            try:
                tweet.retweet()
                cnt_retweeted += 1
                print(f'Retweeted {url}')
            except tweepy.error.TweepError as e:
                print('TweepyError {0}'.format(e))
                # [{'code': 185, 
                # 'message': 'User is over daily status update limit.'}]
                if e.api_code == 185:
                    still_going = False
                    break
        if still_going is False:
            break
    print('retweeted {0}'.format(cnt_retweeted))
    

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str,
                        default='config.yaml',
                        help='The configuration file path')
    FLAGS, _ = parser.parse_known_args()

    FLAGS.config = os.path.abspath(os.path.expanduser(FLAGS.config))

    main()

