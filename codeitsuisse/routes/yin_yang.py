import logging
from decimal import Decimal

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)


@app.route('/yin-yang', methods=['POST'])
def evaluate_yy():
    """
    {
        "number_of_elements" : n,
        "number_of_operations" : k,
        "elements" :  E,
    }
    :return:
    """

    data = request.get_json()
    logger.info(f"yin-yang data: {data}")
    n = data["number_of_elements"]
    k = data["number_of_operations"]
    elements = data["elements"]

    s = Solution()
    result = float(s.yy(elements, k))

    return jsonify(result)


class Solution:
    def __init__(self):
        self.memo = {}

    def yy(self, elem, k):
        # check memo
        if elem in self.memo:
            return self.memo[elem]

        # base case
        if k == 0:
            return Decimal(0)

        # recursive
        expected_yang = Decimal(0)
        for i in range(len(elem)):

            # choose most rational decision
            left_elem = elem[:i] + elem[i + 1:]
            right = len(elem) - 1 - i
            right_elem = elem[:right] + elem[right + 1:]

            if elem[i] == "Y" and elem[right] != "Y":
                left_yang = self.yy(left_elem, k-1) + Decimal(1)
                expected_yang += left_yang / Decimal(len(elem))
            elif elem[i] != "Y" and elem[right] == "Y":
                right_yang = self.yy(right_elem, k-1) + Decimal(1)
                expected_yang += right_yang / Decimal(len(elem))
            elif left_elem == right_elem:
                left_yang = self.yy(left_elem, k-1) + Decimal(1)
                expected_yang += left_yang / Decimal(len(elem))
            else:
                left_yang = self.yy(left_elem, k - 1)
                right_yang = self.yy(right_elem, k - 1)
                if elem[i] == "Y":
                    left_yang += Decimal(1)
                if elem[right] == "Y":
                    right_yang += Decimal(1)

                yang = (left_yang + right_yang) / Decimal(2)
                expected_yang += yang / Decimal(len(elem))

        # keep solution to current search node
        if elem not in self.memo:
            self.memo[elem] = expected_yang

        return expected_yang
