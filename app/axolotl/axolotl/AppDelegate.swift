//
//  AppDelegate.swift
//  Axolotl
//
//  Created by Gregory Foster on 9/2/17.
//  Copyright © 2017 Greg M Foster. All rights reserved.
//

import UIKit

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions
                     launchOptions: [UIApplicationLaunchOptionsKey: Any]?) -> Bool {
        let testViewController = ViewController()
        self.window = UIWindow(frame: UIScreen.main.bounds)
        self.window!.rootViewController = testViewController
        self.window!.backgroundColor = UIColor.white
        self.window!.makeKeyAndVisible()
        return true
    }
}
