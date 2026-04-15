% Manuscript values for the MN draft.
% This file is intentionally TeX-only so it can be loaded with \input{values.md}.

% Core experiment summary
\newcommand{\valNonlinearBefore}{46.7\%}
\newcommand{\valNonlinearAfter}{3.84\%}
\newcommand{\valNonlinearSuppression}{95.41\%}
\newcommand{\valSensitivityDriftSuppression}{93.95\%}
\newcommand{\valFnDriftSuppression}{96.45\%}
\newcommand{\valSensitivityDriftSuppressionLI}{65.30\%}
\newcommand{\valNonlinearSuppressionSUN}{88.66\%}
\newcommand{\valCompImprove}{11.22\%}
\newcommand{\valSpeedup}{2.1}

% Scan settings
\newcommand{\valFreqScanStart}{10}
\newcommand{\valFreqScanEnd}{128}
\newcommand{\valFreqScanPoints}{13}
\newcommand{\valMagScanStart}{0.24}
\newcommand{\valMagScanEnd}{6.0}
\newcommand{\valMagScanPoints}{25}
\newcommand{\valScanSeconds}{4}
\newcommand{\valCalibrationTableFreqStart}{5}
\newcommand{\valCalibrationTableFreqEnd}{200}
\newcommand{\valSequenceNum}{8000}
\newcommand{\valSamplingFreq}{2000}

% Training settings
\newcommand{\valInitLR}{0.002}
\newcommand{\valEpochs}{30000}
\newcommand{\valBatchSize}{260000}
\newcommand{\valSliceDivisor}{2}
\newcommand{\valCosinePeriod}{100}
\newcommand{\valRestartPeriod}{5000}
\newcommand{\valLrDecay}{0.9}
\newcommand{\valMaeWeight}{0.2}

% Prior MET operating data cited in the introduction
\newcommand{\valXuBandwidthStart}{0.7}
\newcommand{\valXuBandwidthEnd}{100}
\newcommand{\valXuPeakSensitivity}{6221}
\newcommand{\valXuPeakSensitivityFreq}{3}
\newcommand{\valXuLinearLimitMm}{1.0}
\newcommand{\valXuLinearLimitAcc}{0.13}
\newcommand{\valSunLinearLimitMm}{0.7}
\newcommand{\valSunLinearLimitAcc}{0.09}
\newcommand{\valLiForceMm}{1.8}
\newcommand{\valLiForceFreqA}{1}
\newcommand{\valLiForceAccA}{0.011}
\newcommand{\valLiForceFreqB}{5}
\newcommand{\valLiForceAccB}{0.057}
\newcommand{\valSunForceMm}{3.7}
\newcommand{\valSunForceFreq}{20}
\newcommand{\valSunForceAcc}{0.46}

% Nonlinear frequency-response drift example
\newcommand{\valMetFnMin}{34.2}
\newcommand{\valMetFnMax}{93.4}
\newcommand{\valMetFnDriftPct}{173.1\%}
\newcommand{\valMetSensMin}{60.6}
\newcommand{\valMetSensMax}{203.4}
\newcommand{\valMetSensDriftPct}{254.6\%}
\newcommand{\valLrnnStateDim}{4}
\newcommand{\valIirOrder}{2}
\newcommand{\valInputGainExpansion}{10}

% Experimental setup table
\newcommand{\valTableDistortion}{1\%}
\newcommand{\valAcquisitionResolution}{16-bit}
\newcommand{\valEnvironmentTemperature}{25^\circ\text{C}}
\newcommand{\valReadoutAmplifier}{AD706}
\newcommand{\valTestSampleModel}{MTSS-1001}
\newcommand{\valNormMin}{-1}
\newcommand{\valNormMax}{1}

% Wiener-KAN hyperparameters selected for the reported run
\newcommand{\valSplineGridCount}{8}
\newcommand{\valSplineOrder}{2}
\newcommand{\valFrikanVariantSmall}{Wiener-KANh6u6l3}
\newcommand{\valFrikanVariantMedium}{Wiener-KANh6u6l4}
\newcommand{\valFrikanVariantLarge}{Wiener-KANh8u6l6}

% Model comparison table
\newcommand{\valWienerIONS}{46.29\%}
\newcommand{\valWienerSDS}{55.54\%}
\newcommand{\valWienerNFDS}{-18.37\%}
\newcommand{\valGRUSmallIONS}{86.70\%}
\newcommand{\valGRUSmallSDS}{76.47\%}
\newcommand{\valGRUSmallNFDS}{91.33\%}
\newcommand{\valGRUSmallParams}{1,201}
\newcommand{\valFrikanSmallIONS}{95.34\%}
\newcommand{\valFrikanSmallSDS}{92.59\%}
\newcommand{\valFrikanSmallNFDS}{95.67\%}
\newcommand{\valFrikanSmallParams}{1,303}
\newcommand{\valLSTMSmallIONS}{89.74\%}
\newcommand{\valLSTMSmallSDS}{84.32\%}
\newcommand{\valLSTMSmallNFDS}{92.95\%}
\newcommand{\valLSTMSmallParams}{1,441}
\newcommand{\valFrikanMediumIONS}{95.41\%}
\newcommand{\valFrikanMediumSDS}{93.95\%}
\newcommand{\valFrikanMediumNFDS}{96.45\%}
\newcommand{\valFrikanMediumParams}{1,669}
\newcommand{\valGRUMediumIONS}{78.96\%}
\newcommand{\valGRUMediumSDS}{84.57\%}
\newcommand{\valGRUMediumNFDS}{91.06\%}
\newcommand{\valGRUMediumParams}{2,179}
\newcommand{\valFrikanLargeIONS}{94.30\%}
\newcommand{\valFrikanLargeSDS}{93.14\%}
\newcommand{\valFrikanLargeNFDS}{96.59\%}
\newcommand{\valFrikanLargeParams}{2,569}
\newcommand{\valRVTDCNNIONS}{81.77\%}
\newcommand{\valRVTDCNNSDS}{77.58\%}
\newcommand{\valRVTDCNNNFDS}{93.82\%}
\newcommand{\valRVTDCNNParams}{2,595}
\newcommand{\valLSTMLargeIONS}{72.20\%}
\newcommand{\valLSTMLargeSDS}{85.40\%}
\newcommand{\valLSTMLargeNFDS}{91.51\%}
\newcommand{\valLSTMLargeParams}{2,641}

% Embedded deployment results
\newcommand{\valTargetMcu}{STM32F405}
\newcommand{\valFrikanLatencyRaw}{2.805}
\newcommand{\valFrikanLatencyLUT}{0.113}
\newcommand{\valLSTMLatency}{0.347}
\newcommand{\valLutPoints}{800}
\newcommand{\valLutTargetMae}{0.005}
\newcommand{\valLutFlashKB}{550}
\newcommand{\valLutAccuracyLossMax}{0.5\%}
\newcommand{\valLatencyPointCount}{1000}
\newcommand{\valSensitivityCompareFreq}{100}

% Additional literature and illustration values
\newcommand{\valLinearLimitRefFreq}{20}
\newcommand{\valThermocoupleNonlinearBefore}{2.03\%}
\newcommand{\valThermocoupleNonlinearAfter}{0.002\%}
\newcommand{\valKanExampleCoeffA}{\frac{1}{3}}
\newcommand{\valKanExampleCoeffB}{\frac{1}{6}}
\newcommand{\valKanExampleEpochA}{10}
\newcommand{\valKanExampleEpochB}{30}
\newcommand{\valKanExampleEpochC}{50}
