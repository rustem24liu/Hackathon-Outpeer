


def second_largest(nums):
    unique = list(set(nums))
    if len(unique) < 2:
        return None
    unique.sort(reverse=True)
    return unique[1]


dataset = [12, 45, 3, 45, 23, 89, 89, 5, 34]

result = second_largest(dataset)
print("Второе по величине число в списке:", result)