import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import argparse


def load(worklist):
      df=pd.read_csv(worklist+'_pic_pang_nextc_covert.qc.csv')
      ct=pd.read_csv(worklist+'_ct.csv')
      ss=pd.read_csv('../SampleSheet.csv', skiprows=19)
      all = pd.merge(left=ss, right=df, left_on='Sample_ID', right_on='case')
      all = pd.merge(left=all, right=ct, left_on='case', right_on='case')
      all['colour']="Red"
      all.loc[all.qc_pass==True, 'colour']="Green"
      return all


def undeterminedTo42(all):
      all.loc[all['Beta-CoV-E Gene']=='Undetermined','Beta-CoV-E Gene'] = 42
      all.loc[all['SARS-CoV-2 S Gene']=='Undetermined','SARS-CoV-2 S Gene'] = 42
      all['Beta-CoV-E Gene'] = pd.to_numeric(all['Beta-CoV-E Gene'])
      all['SARS-CoV-2 S Gene'] = pd.to_numeric(all['SARS-CoV-2 S Gene'])
      return all


def scatterPlotLinReg(data, x_col, y_col, plot_name):
      X = data.loc[data[y_col] < 42, x_col].values.reshape(-1, 1)  # values converts it into a numpy array
      Y = data.loc[data[y_col] < 42, y_col].values.reshape(-1, 1)  # -1 means that calculate the dimension of rows, but have 1 column
      linear_regressor = LinearRegression()  # create object for the class
      linear_regressor.fit(X, Y)  # perform linear regression
      Y_pred = linear_regressor.predict(X)  # make predictions
      plt.scatter(data.loc[:,x_col], data.loc[:,y_col], c=data.colour)
      plt.title(label=plot_name.replace('_', ' ').replace('.png', ''))
      plt.plot(X, Y_pred, color='blue')
      plt.axhline(y=33, color='orange', linestyle='-')
      plt.savefig(plot_name)
      plt.close()



if __name__ == "__main__":

      parser = argparse.ArgumentParser()
      parser.add_argument("-a", "--arctic", nargs=1, type=str, help="full path to artice pipeline output folder", required=True)
      parser.add_argument("-w", "--worklist", nargs=1, type=str, help="Name of the run/worklist", required=True)
      args = parser.parse_args()

      os.chdir(args.arctic[0])

      all = load(args.worklist[0])
      all = undeterminedTo42(all)
      all['mean_ct'] = all['Beta-CoV-E Gene'] / 2 + all['SARS-CoV-2 S Gene'] / 2

      scatterPlotLinReg(all, "MEDIAN_INSERT_SIZE", "mean_ct", "Insert_size_vs_mean_cT.png") # mean insert size VS mean cT
      scatterPlotLinReg(all, "READ_PAIRS", "mean_ct", "Reads_vs_mean_cT.png") # mean insert size VS mean cT
      scatterPlotLinReg(all, "READ_PAIRS", "SARS-CoV-2 S Gene", "Reads_vs_S_gene_cT.png") # mean insert size VS mean cT
      scatterPlotLinReg(all, "READ_PAIRS", "Beta-CoV-E Gene", "Reads_vs_E_gene_cT.png") # mean insert size VS mean cT

      all.to_csv(args.worklist[0]+"_pic_pang_nextc_CT.qc.csv")