import re

with open('research/optimizer.py', 'r') as f:
    content = f.read()

# Replace the incorrect np.norm call with a robust standard normal approximation or scipy import
old_code = """            euler_mascheroni = 0.5772156649
            sr_peaktrial = (1 - euler_mascheroni) * np.norm.ppf(1 - 1.0 / num_trials) + euler_mascheroni * np.norm.ppf(1 - 1.0 / (num_trials * np.e))"""

new_code = """            euler_mascheroni = 0.5772156649
            # Using scipy.stats.norm for correct inverse CDF calculation
            from scipy.stats import norm
            sr_peaktrial = (1 - euler_mascheroni) * norm.ppf(1 - 1.0 / num_trials) + euler_mascheroni * norm.ppf(1 - 1.0 / (num_trials * np.e))"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('research/optimizer.py', 'w') as f:
        f.write(content)
    print("Successfully patched DSR calculation.")
else:
    print("Could exact-match target block, patching inline.")
