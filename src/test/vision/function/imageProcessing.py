
def findMHighGest( result ):
    max_X = None
    hand_landmark = None
    handedness_ = None

    if result.hand_landmarks:

        for landmark, handedness in zip(result.hand_landmarks, result.handedness):

            if max_X is None:
                hand_landmark = landmark
                handedness_ = handedness
                max_X = landmark[0].y
            else:
                if max_X > landmark[0].y:
                    hand_landmark = landmark
                    max_X = landmark[0].y
                    handedness_ = handedness

    return hand_landmark, handedness_