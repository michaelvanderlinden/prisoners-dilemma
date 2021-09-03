import numpy

# This strategy:
# 1) Plays tit-for-tat (never defects first).
# 2) Detects "deadlocks" of DD,DD or DC,CD and attempts to break out of them by turning the other cheek.
#       Only a couple times though; it stops trying if the opponent repeatedly fails to accept the peace offering.
# 3) Cautiously detects "randos" (opponent flipping a coin for each move) and exploits them through straight Ds.
#       Even with just a handful of randos in the pool, the score boost is substantial (in the end, there were about 10).
#       The random detector is intentionally conservative (opponent has to be super chaotic over 30 rounds to trigger),
#       and it will still revert to normal play if it detects a deadlock against a supposed rando.
#       False positive is worse than false negative.

# This strategy came in second out of 1600, and evidence suggests that the winning strategy was almost identical,
# but with a slightly more aggressive random detector.

# responded_in_kind counts the number of times the opponent responded like a good TFT
def responded_in_kind(hist):
	opp_tft_responses = 0
	for i in range(len(hist[1]) - 1):
		if hist[1][i+1] == hist[0][i]:
			opp_tft_responses += 1
	return opp_tft_responses


def strategy(history, memory):
	if history.shape[1] == 0:
		memory = (0, 3, 0)
	cooldown = memory[0] # two turns of peace to break out of the spiral
	escapes = memory[1]  # opponent has 3 chances to accept a peace offering
	rando = memory[2]    # are we against a rando
	move = 1

	if history.shape[1] == 30: # check rando r30
		oppsum = sum(history[1])
		# opponent with least 8 Cs and 8 Ds, and at least 9 or so non-TFT responses in first 30 rounds means likely random
		if oppsum >= 8 and oppsum <= 22 and responded_in_kind(history) <= 21:
			escapes = 3
			rando = 1

	if rando and history.shape[1] >= 45: # double-check rando after r45
		if sum(history[1][-10:]) == 0:   # deadlock in last 10 turns means calling them random was a mistake
			rando = 0

	if cooldown == 1: # janky way to tell when we're coming off cooldown; decrement escapes
		if history.shape[1] >= 2 and history[1, -1] == 0:
			escapes -= 1
		cooldown = 0

	if rando: # exploit the randos
		move = 0
	elif history.shape[1] >= 1 and history[1, -1] == 0 and not cooldown:
		move = 0 # regular TFT
		# escape from death spirals, both of the straight-Ds and alternating D/C variety
		if history.shape[1] > 4 and escapes > 0:
			if ((history[0, -1] == 0 and history[0, -2] == 0 and history[0, -3] == 0 and history[1, -1] == 0 and history[1, -2] == 0 and history[1, -3] == 0) or
				(history[0, -1] == 1 and history[0, -2] == 0 and history[0, -3] == 1 and history[0, -4] == 0 and history[1, -1] == 0 and history[1, -2] == 1 and history[1, -3] == 0 and history[1, -4] == 1)):
				cooldown = 3
				move = 1
	
	if cooldown > 0:
		cooldown -= 1
	memory = (cooldown, escapes, rando)
	return move, memory
