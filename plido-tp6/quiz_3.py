import statistics as st

samples = [-0.5 for n in range(98)]
for n in range(2):
    samples.append(100)

print("Mean =", st.mean(samples))
print("Median =", st.median(samples))

q = st.quantiles(samples)
print("Quartiles:", q)
ecart = q[2] - q[0]
print("Ecart Interquartile =", ecart)

