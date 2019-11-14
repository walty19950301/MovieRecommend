
import MovieDataset as md, WQUtil as util, RA

util.log('Main', 'start')
movies = md.Movies('..\\ml_ra\\movies.dat')
ratings = md.Ratings('..\\ml_ra\\ratings.dat')
ra = RA.RA(movies,ratings)
ra.process()
del ra
del movies
del ratings
util.log('Main', 'end')
