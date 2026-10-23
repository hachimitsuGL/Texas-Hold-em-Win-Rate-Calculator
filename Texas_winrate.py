from collections import Counter

SUITS = ["spade", "heart", "diamond", "club"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]


class Card:

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    @property
    def suit(self):
        return self._suit

    @suit.setter
    def suit(self, value):
        if value not in SUITS:
            raise ValueError("Card suit must be spade, heart, diamond or club")
        self._suit = value

    @property
    def rank(self):
        return self._rank

    @rank.setter
    def rank(self, value):
        if value not in RANKS:
            raise ValueError("Card rank must be 2,3,4,5,6,7,8,9,T,J,Q,K,A")
        self._rank = value


def is_straightflush(set):
    flush_counts = Counter(card.suit for card in set)
    # find out which suit has 5 or more cards
    flush_suit = [suit for suit, count in flush_counts.items() if count >= 5]
    if flush_suit == []:
        return False
    else:
        result_set = []
        for i in set:
            if i.suit == flush_suit[0]:
                result_set.append(i)
        if is_straight(result_set) != False:
            return is_straight(result_set)
        else:
            return False


def is_fourofakind(set):
    rank_counts = Counter(card.rank for card in set)
    # find out which rank has 4 cards
    four_rank = [rank for rank, count in rank_counts.items() if count == 4]
    if four_rank == []:
        return False
    else:
        result_set = []
        for i in set:
            if i.rank == four_rank[0]:
                result_set.append(i)
        return result_set


def is_fullhouse(set):
    three_cards = is_threeofakind(set)
    if three_cards is False:
        return False
    remaining = [card for card in set if card.rank != three_cards[0].rank]
    pair_cards = is_onepair(remaining)
    if pair_cards is False:
        return False
    return three_cards + pair_cards


# フラッシュである場合returnその最大 flush set、ではない場合return False
def is_flush(set):
    flush_counts = Counter(card.suit for card in set)
    # find out which suit has 5 or more cards
    flush_suit = [suit for suit, count in flush_counts.items() if count >= 5]
    if flush_suit == []:
        return False
    else:
        result_set = []
        for i in set:
            if i.suit == flush_suit[0]:
                result_set.append(i)
        return remove_lowcards(result_set)


# straightである場合return最大のstraight、ではない場合return False
def is_straight(set):
    rank_to_num = {RANKS.index(card.rank) + 2: card for card in set}

    if 14 in rank_to_num:
        rank_to_num[1] = rank_to_num[14]

    for high in range(14, 4, -1):
        needed = range(high - 4, high + 1)
        if all(rank in rank_to_num for rank in needed):
            return [rank_to_num[rank] for rank in needed]

    return False


def is_threeofakind(set):
    sorted_set = sorted(set, key=lambda x: RANKS.index(x.rank))
    rank_counts = Counter(card.rank for card in sorted_set)
    # find out which rank has 3 cards
    three_rank = [rank for rank, count in rank_counts.items() if count == 3]
    if three_rank == []:
        return False
    else:
        result_set = []
        for i in set:
            if i.rank == three_rank[-1]:
                result_set.append(i)
        return result_set


def is_twopairs(set):
    first_pair = is_onepair(set)
    if first_pair is False:
        return False
    remaining = [card for card in set if card.rank != first_pair[0].rank]
    second_pair = is_onepair(remaining)
    if second_pair is False:
        return False
    return first_pair + second_pair


def is_onepair(set):
    sorted_set = sorted(set, key=lambda x: RANKS.index(x.rank))
    rank_counts = Counter(card.rank for card in sorted_set)
    # find out which rank has 2 cards
    two_rank = [rank for rank, count in rank_counts.items() if count >= 2]
    if two_rank == []:
        return False
    else:
        result_set = []
        for i in set:
            if i.rank == two_rank[-1]:
                result_set.append(i)
        return result_set[:2]


# この関数は、5個のcardを超えるsetの最大の5個のcardを選び出す
def remove_lowcards(set):
    sorted_set = sorted(set, key=lambda x: RANKS.index(x.rank))
    while True:
        if len(sorted_set) <= 5:
            return sorted_set
        else:
            del sorted_set[0]


POKER_HANDS = [
    "straight_flush",
    "four_of_a_kind",
    "full_house",
    "flush",
    "straight",
    "three_of_a_kind",
    "two_pairs",
    "one_pair",
    "high_card",
]
def add_kickers(result_set, original_set):
    remaining = [card for card in original_set if card not in result_set]
    remaining = sorted(remaining, key=lambda x: RANKS.index(x.rank), reverse=True)
    return result_set + remaining[:5-len(result_set)]

# lenth of card_set must = 2,5,6,7
def max_combin(set):
    if len(set) not in (2, 5, 6, 7):
        raise ValueError("lenth of card_set must = 2,5,6,7")

    if is_straightflush(set) is not False:
        return is_straightflush(set), POKER_HANDS[0]

    elif is_fourofakind(set) is not False:
        return add_kickers(is_fourofakind(set), set), POKER_HANDS[1]

    elif is_fullhouse(set) is not False:
        return is_fullhouse(set), POKER_HANDS[2]

    elif is_flush(set) is not False:
        return is_flush(set), POKER_HANDS[3]

    elif is_straight(set) is not False:
        return is_straight(set), POKER_HANDS[4]

    elif is_threeofakind(set) is not False:
        return add_kickers(is_threeofakind(set), set), POKER_HANDS[5]

    elif is_twopairs(set) is not False:
        return add_kickers(is_twopairs(set), set), POKER_HANDS[6]

    elif is_onepair(set) is not False:
        return add_kickers(is_onepair(set), set), POKER_HANDS[7]

    else:
        return remove_lowcards(set), POKER_HANDS[8]

def hand_value(cards, hand_type):
    values = [RANKS.index(card.rank) + 2 for card in cards]

    if hand_type in ("straight", "straight_flush"):
        if set(values) == {14, 2, 3, 4, 5}:
            return (5,)
        return (max(values),)

    counts = Counter(values)

    return tuple(sorted(
        values,
        key=lambda x: (counts[x], x),
        reverse=True
    ))

# if set1 win return 1;elif set2 win return -1;else return 0
def compare_set(set1, set2):
    cards1, type1 = max_combin(set1)
    cards2, type2 = max_combin(set2)

    rank1 = POKER_HANDS.index(type1)
    rank2 = POKER_HANDS.index(type2)

    
    if rank1 != rank2:
        return 1 if rank1 < rank2 else -1

    
    value1 = hand_value(cards1, type1)
    value2 = hand_value(cards2, type2)

    if value1 > value2:
        return 1
    elif value1 < value2:
        return -1
    else:
        return 0


# def print_set(set):
#     if isinstance(set, bool):
#         print("NULL!")
#         return
#     for i in set:
#         print(i.suit + i.rank)


# testset = [
#     Card(SUITS[0], RANKS[12]),
#     Card(SUITS[1], RANKS[0]),
#     Card(SUITS[0], RANKS[1]),
#     Card(SUITS[1], RANKS[2]),
#     Card(SUITS[0], RANKS[3]),
#     Card(SUITS[3], RANKS[6]),
#     Card(SUITS[3], RANKS[12]),
# ]
# print_set(is_straight(testset))
