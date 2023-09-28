import numpy as np
import matplotlib.pyplot as plt

# Note this takes a while with math functions, also with multiple axies it is somewhat difficult to precisely determine panting in a specific direction
# so I've just measured the magnitue of the change in acceleration with respect to all axies and also just the magnitue of acceleration as well as printing the gradient vector.


# For anyone reading this, I have found the magnitude of gradient to be the most descriptive and looks promiseing to find breath frequency (second last number),
# when it is zero the sheep should not be accelerating and when it is positive the sheep should either be accelerating forwards or backwards (look at gradient vector to distinguish)


cleanedFile = "test_data/sheep1_cleaned_data/sheep1.csv"
with open(cleanedFile, 'r') as file:
    index = 0
    next(file)
    next(file)
    
    startIndex = 1002000
    numLines = 500
    endIndex = startIndex + numLines
    
    gradientMagnitudes = []
    
    sumVector = np.array([0,0,0])
    prevVector = np.array([0, 0, 0])
    
    # For eigenvector calculations
    # for line in file:
    #     if index < startIndex:
    #         pass
    #     elif index < endIndex:
    #         XYZ = line.split(',')
    #         vector = np.array([int(XYZ[0]), int(XYZ[1]), int(XYZ[2])])
    #         sumVector = np.add(sumVector, vector)
    
    print("X, Y, Z, Seconds")
    for line in file:
        if index < startIndex:
            pass
        elif index < endIndex:
            XYZ = line.split(',')
            vector = np.array([int(XYZ[0]), int(XYZ[1]), int(XYZ[2])])
            
            gVector = np.array([vector[0] - prevVector[0], vector[1] - prevVector[1] , vector[2] - prevVector[2]])

            gMag = np.linalg.norm(gVector)
            # magPrev = np.linalg.norm(prevVector)
            # mag = np.linalg.norm(vector)
            
            prevVector[0] = vector[0]
            prevVector[1] = vector[1]
            prevVector[2] = vector[2]
            
            if index == startIndex:
                #print(XYZ[-1], vector, "N/A", "N/A")
                pass
            else:
                gradientMagnitudes.append(gMag)
                #print(XYZ[-1], vector, gVector, gMag)
        
        index += 1
    
    print(sumVector)
    points = np.array(gradientMagnitudes)
    plt.plot(points)
    plt.show()