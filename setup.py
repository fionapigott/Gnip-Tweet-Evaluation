from distutils.core import setup

setup(
    name='gnip_tweet_evaluator',
    version='0.1.0',
    author='Jeff Kolb',
    author_email='jeffakolb@gmail.com',
    packages=['gnip_tweet_evaluator'],
    scripts=['evaluate_tweets.py'],
    url='https://github.com/jeffakolb/',
    download_url='https://github.com/jeffakolb/Gnip-Tweet-Evaluation/tags/',
    license='LICENSE.txt',
    description='Conversation and audience analysis of a corpus of Tweet payloads from Gnip/Twitter APIs.', 
    install_requires=[]
    )
