def get_score_from(ltv, return_period_month):
	ltv_score = 0
	if ltv <= 30:
		ltv_score = 50
	elif ltv <= 50:
		ltv_score = 40
	elif ltv <= 60:
		ltv_score = 30
	elif ltv <= 70:
		ltv_score = 10

	return_score = 0
	if return_period_month <= 3:
		return_score = 50
	elif return_period_month <= 5:
		return_score = 40
	elif return_period_month <= 6:
		return_score = 30
	elif return_period_month <= 9:
		return_score = 20
	elif return_period_month <= 12:
		return_score = 10

	return ltv_score + return_score
