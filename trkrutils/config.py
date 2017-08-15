datasets = {
    'otb_v1.0': {
        'url_prefix': 'http://cvlab.hanyang.ac.kr/tracker_benchmark/seq',
        # The "Jogging" video is for multiple objects tracking, not support in our module
        'videos': [
            'Basketball', 'Bolt', 'Boy', 'Car4', 'CarDark', 'CarScale', 'Coke', 'Couple', 'Crossing', 'David',
            'David2', 'David3', 'Deer', 'Dog1', 'Doll', 'Dudek', 'FaceOcc1', 'FaceOcc2', 'Fish', 'FleetFace',
            'Football', 'Football1', 'Freeman1', 'Freeman3', 'Freeman4', 'Girl', 'Ironman', 'Jumping', 'Lemming', 'Liquor',
            'Matrix', 'Mhyang', 'MotorRolling', 'MountainBike', 'Shaking', 'Singer1', 'Singer2', 'Skating1', 'Skiing', 'Soccer',
            'Subway', 'Suv', 'Sylvester', 'Tiger1', 'Tiger2', 'Trellis', 'Walking', 'Walking2', 'Woman'
        ]
    },
    'vot2013': {
        'url': 'http://data.votchallenge.net/vot2013/vot2013.zip'
    },
    'vot2014': {
        'url': 'http://data.votchallenge.net/vot2014/vot2014.zip'
    },
    'vot2015': {
        'url': 'http://data.votchallenge.net/vot2015/vot2015.zip'
    },
    'vot2016': {
        'url': 'http://data.votchallenge.net/vot2016/vot2016.zip'
    }
}
