import pandas as pd
from sklearn.linear_model import LinearRegression

# Load the Excel file
df = pd.read_excel("C:/Users/username/Desktop/0726  오차 실험.xlsx")  # username을 사용자의 유저네임으로 변경해주세요

# Fill missing values with 0
df_filled = df.fillna(0)

# Prepare the data
X_filled = df_filled[['x', 'y']]
y_x_filled = df_filled['cam x']
y_y_filled = df_filled['cam y']

# Create regression models
reg_x_filled = LinearRegression().fit(X_filled, y_x_filled)
reg_y_filled = LinearRegression().fit(X_filled, y_y_filled)

# Get the coefficients and intercepts
coef_x_filled, intercept_x_filled = reg_x_filled.coef_, reg_x_filled.intercept_
coef_y_filled, intercept_y_filled = reg_y_filled.coef_, reg_y_filled.intercept_

def correct_coordinates(x, y):
    corrected_x = coef_x_filled[0] * x + coef_x_filled[1] * y + intercept_x_filled
    corrected_y = coef_y_filled[0] * x + coef_y_filled[1] * y + intercept_y_filled
    return corrected_x, corrected_y