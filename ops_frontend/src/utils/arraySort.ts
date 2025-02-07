export function compare(propertyName: any) {
    return function (object1: any, object2: any) {
        let value1 = object1[propertyName]
        let value2 = object2[propertyName]
        if (value2 < value1) {
            return 1
        } else if (value2 > value1) {
            return -1
        } else {
            return 0
        }
    }
}