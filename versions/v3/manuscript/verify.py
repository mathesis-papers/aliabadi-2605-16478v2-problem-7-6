import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations
import json
from math import comb, factorial
from pathlib import Path


def make_table(elements, operation):
    lookup = {element: index for index, element in enumerate(elements)}
    return [[lookup[operation(left, right)] for right in elements] for left in elements]


def symmetric_three():
    elements = list(permutations(range(3)))
    table = make_table(elements, lambda left, right: tuple(left[right[index]] for index in range(3)))
    return 'S3', [''.join(str(value + 1) for value in element) for element in elements], table, 3


def dihedral_eight():
    elements = [(rotation, reflection) for reflection in range(2) for rotation in range(4)]
    table = make_table(elements, lambda left, right: (
        (left[0] + (-1 if left[1] else 1) * right[0]) % 4,
        (left[1] + right[1]) % 2,
    ))
    return 'D8', ['1', 'r', 'r^2', 'r^3', 's', 'rs', 'r^2s', 'r^3s'], table, 2


def quaternion_eight():
    elements = [(sign, basis) for sign in (1, -1) for basis in range(4)]
    def multiply(left, right):
        left_sign, left_basis = left
        right_sign, right_basis = right
        sign = left_sign * right_sign
        if left_basis == 0:
            return sign, right_basis
        if right_basis == 0:
            return sign, left_basis
        if left_basis == right_basis:
            return -sign, 0
        if (left_basis, right_basis) not in [(1, 2), (2, 3), (3, 1)]:
            sign = -sign
        return sign, 6 - left_basis - right_basis
    table = make_table(elements, multiply)
    return 'Q8', ['1', 'i', 'j', 'k', '-1', '-i', '-j', '-k'], table, 4


def subgroup_generated(generators, table):
    subgroup = {0}
    frontier = [0]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            product = table[current][generator]
            if product not in subgroup:
                subgroup.add(product)
                frontier.append(product)
    return subgroup


def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for remainder in compositions(total - first, parts - 1):
            yield (first,) + remainder


def abelian_subgroup_checks(table, derived, realizable):
    size = len(table)
    subgroup_count = 0
    multiset_count = 0
    for extra_size in range(size):
        for extra in combinations(range(1, size), extra_size):
            subgroup = (0,) + extra
            members = set(subgroup)
            if any(table[left][right] not in members or table[left][right] != table[right][left]
                   for left in subgroup for right in subgroup):
                continue
            subgroup_count += 1
            block_size = len(subgroup)
            def product(counts):
                result = 0
                for element, count in zip(subgroup, counts):
                    for copy in range(count):
                        result = table[result][element]
                return result
            blocks = [counts for counts in compositions(block_size, block_size) if product(counts) == 0]
            @lru_cache(maxsize=None)
            def partitions_into_blocks(counts):
                if not any(counts):
                    return True
                for block in blocks:
                    if all(part <= count for part, count in zip(block, counts)):
                        remainder = tuple(count - part for part, count in zip(block, counts))
                        if partitions_into_blocks(remainder):
                            return True
                return False
            obstruction_found = False
            for counts in compositions(size, block_size):
                total_product = product(counts)
                partition_exists = partitions_into_blocks(counts)
                assert partition_exists == (total_product == 0)
                full_counts = [0] * size
                for element, count in zip(subgroup, counts):
                    full_counts[element] = count
                assert partition_exists == (tuple(full_counts) in realizable)
                if total_product in derived and not partition_exists:
                    obstruction_found = True
                multiset_count += 1
            assert obstruction_found == bool((members & derived) - {0})
            partitions_into_blocks.cache_clear()
    return {'abelian_subgroups': subgroup_count, 'supported_multisets_checked': multiset_count,
            'length': size, 'status': 'pass'}


def check_group(name, labels, table, witness):
    size = len(table)
    assert len(labels) == size
    assert all(table[0][element] == table[element][0] == element for element in range(size))
    assert all(table[table[left][middle]][right] == table[left][table[middle][right]]
               for left in range(size) for middle in range(size) for right in range(size))
    inverses = [next(candidate for candidate in range(size)
                     if table[element][candidate] == table[candidate][element] == 0)
                for element in range(size)]
    commutators = {
        table[table[table[left][right]][inverses[left]]][inverses[right]]
        for left in range(size) for right in range(size)
    }
    derived = subgroup_generated(commutators, table)
    assert witness != 0 and witness in derived
    target = tuple(size - 1 if element == 0 else 1 if element == witness else 0
                   for element in range(size))
    quotient_table = [[table[image][inverses[point]] for image in range(size)]
                      for point in range(size)]
    realizable = set()
    realizing_counts = Counter()
    support_histogram = Counter()
    target_count = 0
    for permutation in permutations(range(size)):
        counts = [0] * size
        support = 0
        for point, image in enumerate(permutation):
            counts[quotient_table[point][image]] += 1
            support += point != image
        signature = tuple(counts)
        realizable.add(signature)
        realizing_counts[signature] += 1
        support_histogram[support] += 1
        target_count += signature == target
    assert sum(support_histogram.values()) == factorial(size)
    assert support_histogram[1] == 0 and target_count == 0
    sparse_cases = 0
    two_letter_cases = 0
    for first in range(size):
        for second in range(size):
            if first == second:
                continue
            relative = table[inverses[first]][second]
            order = next(exponent for exponent in range(1, size + 1)
                         if power(relative, exponent, table) == 0)
            projected_order = next(exponent for exponent in range(1, size + 1)
                                   if power(relative, exponent, table) in derived)
            for copies in range(size + 1):
                counts = [0] * size
                counts[first] = size - copies
                counts[second] = copies
                assert (tuple(counts) in realizable) == (copies % order == 0)
                expected = comb(size // order, copies // order) if copies % order == 0 else 0
                assert realizing_counts[tuple(counts)] == expected
                product = table[power(first, size - copies, table)][power(second, copies, table)]
                assert (product in derived) == (copies % projected_order == 0)
                two_letter_cases += 1
                sparse_cases += first == 0
    return {
        'group': name,
        'order': size,
        'labels': labels,
        'commutator_subgroup': [labels[element] for element in sorted(derived)],
        'witness': {'nonidentity_element': labels[witness], 'identity_multiplicity': size - 1,
                    'nonidentity_multiplicity': 1, 'abelianization_product_identity': True,
                    'realizing_permutations': target_count},
        'permutations_enumerated': factorial(size),
        'distinct_quotient_multisets': len(realizable),
        'permutation_support_histogram': {str(key): value for key, value in sorted(support_histogram.items())},
        'sparse_support_cases': sparse_cases,
        'ordered_two_letter_cases': two_letter_cases,
        'subgroup_criterion': abelian_subgroup_checks(table, derived, realizable),
        'status': 'pass',
    }


def power(element, exponent, table):
    result = 0
    for step in range(exponent):
        result = table[result][element]
    return result


def family_group(rotations, dicyclic=False):
    elements = [(rotation, reflection) for reflection in range(2) for rotation in range(rotations)]
    central = rotations // 2 if dicyclic else 0
    table = make_table(elements, lambda left, right: (
        (left[0] + (-1 if left[1] else 1) * right[0]
         + central * left[1] * right[1]) % rotations,
        (left[1] + right[1]) % 2,
    ))
    name = f'Dic_{rotations // 2}' if dicyclic else f'D{2 * rotations}'
    return name, table, rotations, 2 * rotations - 1, 2


def alternating_four():
    elements = [element for element in permutations(range(4))
                if sum(element[left] > element[right]
                       for left in range(4) for right in range(left + 1, 4)) % 2 == 0]
    table = make_table(elements, lambda left, right: tuple(left[right[index]] for index in range(4)))
    return 'A4', table, elements.index((1, 2, 0, 3)), elements.index((3, 0, 2, 1)), 3


def two_letter_exhaustion(name, table, first, second, first_copies):
    size = len(table)
    assert all(table[0][element] == table[element][0] == element for element in range(size))
    assert all(table[table[left][middle]][right] == table[left][table[middle][right]]
               for left in range(size) for middle in range(size) for right in range(size))
    inverses = [next(candidate for candidate in range(size)
                     if table[element][candidate] == table[candidate][element] == 0)
                for element in range(size)]
    relative = table[inverses[first]][second]
    order = next(exponent for exponent in range(1, size + 1)
                 if power(relative, exponent, table) == 0)
    realized = Counter()
    for choices in range(1 << size):
        images = [table[second if choices & (1 << point) else first][point]
                  for point in range(size)]
        if len(set(images)) != size:
            continue
        for point, image in enumerate(images):
            assert table[image][inverses[point]] == (
                second if choices & (1 << point) else first)
        realized[choices.bit_count()] += 1
    assert set(realized) == set(range(0, size + 1, order))
    assert sum(realized.values()) == 2 ** (size // order)
    assert all(realized[copies] == (comb(size // order, copies // order)
                                   if copies % order == 0 else 0)
               for copies in range(size + 1))
    assert table[power(first, first_copies, table)][power(second, size - first_copies, table)] == 0
    assert realized[size - first_copies] == 0
    return {
        'group': name, 'order': size, 'maps_enumerated': 1 << size,
        'relative_element_order': order,
        'first_label_index': first, 'second_label_index': second,
        'witness_multiplicities': [first_copies, size - first_copies],
        'product_one_ordering': 'First all copies of the first label, then all copies of the second.',
        'realizing_permutations_by_second_multiplicity': {
            str(copies): count for copies, count in sorted(realized.items())},
        'witness_realizing_permutations': 0, 'status': 'pass',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    arguments = parser.parse_args()
    result = {
        'schema_version': 1,
        'coverage': 'Exhaustive permutation checks in S3, D8 and Q8, all ordered two-letter supports and multiplicities, all abelian subgroups at ambient group length, and exhaustive two-letter-map checks for the specified dihedral, dicyclic and A4 examples.',
        'groups': [check_group(*group()) for group in [symmetric_three, dihedral_eight, quaternion_eight]],
        'product_one_families': [two_letter_exhaustion(*group) for group in (
            [family_group(rotations) for rotations in range(3, 9)]
            + [family_group(2 * parameter, True) for parameter in range(2, 5)]
            + [alternating_four()])],
        'general_results': 'The note gives written proofs for arbitrary finite groups and the abelian-subgroup criterion.',
        'status': 'pass',
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if arguments.output:
        arguments.output.write_text(rendered)
    else:
        print(rendered, end='')


if __name__ == '__main__':
    main()
