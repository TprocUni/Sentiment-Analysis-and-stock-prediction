# Sentiment-Analysis-and-stock-prediction
This project integrates Stock Correlation Networks (SCNs) and Natural Language Processing (NLP) for sentiment analysis to predict stock movements. It highlights how public sentiment affects not just individual stocks but spreads to related ones, offering a novel prediction tool for individual investors.


The project examines the link between public sentiment and stock market behavior, leveraging **Stock Correlation Networks (SCNs)** and **Natural Language Processing (NLP)** with sentiment analysis. The primary hypothesis suggests that public sentiment, derived from media and news sources, impacts not only individual stock performance but also propagates to related stocks within the same industry or index. This insight serves as the foundation for a predictive tool aimed at empowering individual investors with analytical capabilities traditionally reserved for institutional investors.

#### Methodology:
1. **Data Collection**:
   - Financial data for stock movements and related news articles were gathered to serve as input for analysis.
   
2. **Sentiment Analysis**:
   - Using tools like **VADER** and **TextBlob**, news articles were analyzed to determine sentiment polarity (positive, neutral, or negative).
   - Sentiment scores were then linked to corresponding stock movements.

3. **Stock Correlation Networks**:
   - SCNs were constructed with nodes representing stocks and edges representing correlations between them.
   - Various correlation metrics (e.g., Pearson and Spearman coefficients) were tested to model inter-stock relationships effectively.
   - Sentiment scores from sentiment analysis were propagated through SCNs, simulating how public sentiment impacts correlated stocks.

#### Key Findings:
- SCNs enhance predictive coverage by modeling how sentiment changes in one stock influence related stocks.
- The success of sentiment-based predictions hinges on accurate sentiment analysis and fine-tuned correlation thresholds.
- The tool achieved prediction accuracy surpassing the baseline random walk model (50%), though with room for refinement.

#### Contributions:
- Developed a Python-based framework integrating SCNs and sentiment analysis for short-term stock movement prediction.
- Demonstrated the utility of SCNs in expanding analytical horizons beyond individual stock predictions.
- Highlighted the potential for democratizing access to advanced predictive tools in the financial market.

#### Limitations and Future Work:
- The accuracy of sentiment analysis tools impacts overall performance and requires further improvement.
- SCN scalability and data coverage need testing across broader datasets and timeframes.
- Future iterations could incorporate additional factors like economic indicators or advanced machine learning models.

By combining SCNs and sentiment analysis, the project paves the way for more inclusive and accessible financial analysis tools, empowering individual investors to make data-driven decisions in the dynamic stock market landscape.











