from movie_links_grabbers import ImdbLinkGrabber


grabber = ImdbLinkGrabber()
links = grabber.grab_links(
    "https://www.imdb.com/search/title/?title_type=feature&release_date=1975-01-01,1975-12-31&user_rating=1,10&num_votes=1000,&sort=release_date,desc"
)
grabber.terminate()
for l in links:
    print(l["Name"])
