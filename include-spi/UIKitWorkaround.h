/*
 * UIKit Workaround for iOS SDK compatibility
 * Fixes UIAccessibilityTraits type conflicts
 */

#ifndef UIKitWorkaround_h
#define UIKitWorkaround_h

#import <Foundation/Foundation.h>

// Forward declarations to prevent conflicts
#ifdef __OBJC__

// UIAccessibilityTraits workaround for SDK 16.5+
#ifndef UIAccessibilityTraits
typedef uint64_t UIAccessibilityTraits;
#endif

#endif /* __OBJC__ */

#endif /* UIKitWorkaround_h */

